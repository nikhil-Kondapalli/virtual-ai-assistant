"""
FastAPI LLM Worker - Handles LLM requests via Ollama with RAG and Semantic Caching.
"""

import os
import json
import asyncio
import redis.asyncio as aioredis
from fastapi import FastAPI
import httpx

from rag_service_chroma import initialize_rag_service, process_query_with_rag, close_rag_service

# Config
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/chat")
MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")

# Global state
redis = aioredis.from_url(REDIS_URL)
http_client = httpx.AsyncClient(timeout=None)
stopped_sessions = set()

# Global stop flags for immediate stopping
active_sessions = {}  # Track active session tasks

app = FastAPI()


async def stream_response(session_id: str, prompt: str, persona: str):
    """Stream a response directly from Ollama."""
    full_response = ""
    try:
        async with http_client.stream(
            "POST",
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            }
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                # Check for stop signal
                if session_id in stopped_sessions:
                    print(
                        f"[LLM] 🛑 Stopping generation for session {session_id}")
                    break

                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[LLM] Warning: Could not decode JSON line: {line}")
                    continue

                token = data.get("message", {}).get("content", "")
                if token:
                    full_response += token
                    await redis.publish(
                        f"session:{session_id}:out",
                        json.dumps({
                            "type": "llm_token",
                            "token": token,
                            "persona": persona
                        }),
                    )

                if data.get("done", False):
                    break

    except httpx.RequestError as e:
        print(f"[LLM] Error: Could not connect to Ollama: {e}")
        error_data = {
            "response": str(e),
            "completed": True,
            "error": True
        }
        await redis.publish(f"session:{session_id}:out", json.dumps(error_data))

    finally:
        if session_id in stopped_sessions:
            stopped_sessions.remove(session_id)
            print(f"[LLM] Session {session_id} → Stopped.")
        else:
            await redis.set(f"session:{session_id}:text", full_response)
            print(f"[LLM] Session {session_id} → Finished.")

        await redis.publish(
            f"session:{session_id}:out",
            json.dumps({"type": "llm_end", "persona": persona})
        )


async def handle_message(message_type: str, channel: str, payload: dict):
    """Handle an individual message from Redis."""
    if message_type != "pmessage":
        return

    session_id = channel.split(":")[1]
    prompt = payload.get("prompt")
    persona = payload.get("persona", "kira_v1")  # Default persona

    if not prompt:
        return

    print(f"[LLM] Session {session_id} → Prompt: {prompt}")

    # Check if session was stopped before starting
    if session_id in stopped_sessions:
        stopped_sessions.remove(session_id)
        return

    await process_prompt(session_id, prompt, persona)


async def process_prompt(session_id: str, prompt: str, persona: str):
    """Process a prompt using RAG with fallback to direct Ollama."""
    print(f"🎯 Processing prompt for session {session_id}")

    # Create and track the task
    task = asyncio.create_task(process_with_rag(session_id, prompt, persona))
    active_sessions[session_id] = task

    try:
        await task
    except asyncio.CancelledError:
        print(f"🚫 Task cancelled for session {session_id}")
    except Exception as e:
        print(f"[RAG] Error processing query: {e}")
        # Fallback to original Ollama streaming
        await stream_response(session_id, prompt, persona)
    finally:
        # Clean up
        if session_id in active_sessions:
            del active_sessions[session_id]


async def process_with_rag(session_id: str, prompt: str, persona: str):
    """Process a prompt using the RAG service."""
    print(f"🚀 Starting RAG processing for session {session_id}")

    try:
        async for token in process_query_with_rag(prompt, session_id, stopped_sessions):
            # Check for stop signal IMMEDIATELY
            if session_id in stopped_sessions:
                print(f"🛑 RAG processing stopped for session {session_id}")
                break

            # Handle stop words in token
            if token.lower() in ["[stop]"]:
                break

            # Check stop signal again before publishing
            if session_id in stopped_sessions:
                print(
                    f"🛑 RAG processing stopped for session {session_id} (before publish)")
                break

            await redis.publish(
                f"session:{session_id}:out",
                json.dumps({
                    "type": "llm_token",
                    "token": token,
                    "persona": persona
                })
            )

    except Exception as e:
        print(f"❌ Error in RAG processing for session {session_id}: {e}")

    finally:
        # Send completion message regardless of whether it was stopped or not
        await redis.publish(
            f"session:{session_id}:out",
            json.dumps({"type": "llm_end", "persona": persona})
        )
        if session_id not in stopped_sessions:
            print(f"✅ RAG generation completed for session {session_id}")
        else:
            print(f"🛑 RAG generation stopped for session {session_id}")


async def llm_worker_loop():
    """Main worker loop that processes incoming prompts."""
    pubsub = redis.pubsub()
    await pubsub.psubscribe("session:*:in")

    print("🚀 LLM worker listening for prompts on Redis…")

    async for message in pubsub.listen():
        try:
            channel = message["channel"].decode()
            # Handle Redis ping/subscription messages
            if isinstance(message["data"], int):
                continue

            payload = json.loads(message["data"])
            await handle_message(message["type"], channel, payload)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"[LLM] Error processing message: {e}")


@app.post("/stop/{session_id}")
async def stop_generation(session_id: str):
    """Stop generation for a session."""
    print(f"🛑 STOP REQUESTED for session {session_id}")

    # Add to stopped sessions
    stopped_sessions.add(session_id)
    print(f"📝 Added {session_id} to stopped_sessions: {stopped_sessions}")

    # Cancel any active task for this session
    if session_id in active_sessions:
        task = active_sessions[session_id]
        if not task.done():
            task.cancel()
            print(f"🚫 Cancelled active task for session {session_id}")
        del active_sessions[session_id]

    # Notify TTS worker to stop processing for this session
    await redis.publish(
        "session:control",
        json.dumps({
            "type": "stop_session",
            "session_id": session_id
        })
    )

    print(f"🛑 Stop signal sent for session {session_id}")
    return {"status": "stopped", "session_id": session_id, "stopped_sessions": list(stopped_sessions)}


async def listen_for_control_messages():
    """Listen for control messages on Redis."""
    pubsub = redis.pubsub()
    await pubsub.subscribe("session:control")
    print("🚀 LLM worker listening for control messages on Redis...")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        try:
            data = json.loads(message["data"])
            if data.get("type") == "stop_session":
                session_id = data.get("session_id")
                if session_id:
                    print(f"🛑 STOP REQUESTED for session {session_id}")
                    stopped_sessions.add(session_id)
                    if session_id in active_sessions:
                        task = active_sessions[session_id]
                        if not task.done():
                            task.cancel()
                            print(f"🚫 Cancelled active task for session {session_id}")
                        del active_sessions[session_id]

        except (json.JSONDecodeError, TypeError) as e:
            print(f"[LLM] Error processing control message: {e}")


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    try:
        await initialize_rag_service()
        # Store task reference to prevent garbage collection
        app.state.worker_task = asyncio.create_task(llm_worker_loop())
        app.state.control_task = asyncio.create_task(listen_for_control_messages())
        print("🟢 Startup complete: worker tasks scheduled")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    print("🔌 Closing LLM worker connections...")
    if hasattr(app.state, "worker_task"):
        app.state.worker_task.cancel()
    if hasattr(app.state, "control_task"):
        app.state.control_task.cancel()
    await close_rag_service()
    await http_client.aclose()
    await redis.close()
    print("✅ Services closed")
