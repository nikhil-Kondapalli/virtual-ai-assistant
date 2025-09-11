# """
# FastAPI LLM Worker - Handles LLM requests via Ollama.
# """

import os
import json
import asyncio
import redis.asyncio as aioredis
from fastapi import FastAPI
import httpx

# Config
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")

# Global Redis
redis = aioredis.from_url(REDIS_URL)
stopped_sessions = set()

app = FastAPI()


async def llm_worker_loop():
    pubsub = redis.pubsub()
    await pubsub.psubscribe("session:*:in")

    print("🚀 LLM worker listening for prompts on Redis…")

    async for message in pubsub.listen():
        if message["type"] != "pmessage":
            continue

        channel = message["channel"].decode()
        payload = json.loads(message["data"])
        session_id = channel.split(":")[1]

        prompt = payload.get("prompt")
        persona = payload.get("persona", "kira_v1")  # Default persona
        if not prompt:
            continue

        full_response = ""
        print(f"[LLM] Session {session_id} → Prompt: {prompt}")

        # Check if session was stopped before starting
        if session_id in stopped_sessions:
            stopped_sessions.remove(session_id)
            continue

        try:
            # Stream from Ollama
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    OLLAMA_URL,
                    json={"model": MODEL_NAME, "prompt": prompt, "stream": True},
                ) as response:
                    response.raise_for_status()  # Raise an exception for bad status codes
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
                            print(
                                f"[LLM] Warning: Could not decode JSON line: {line}")
                            continue

                        token = data.get("response")
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
        finally:
            if session_id in stopped_sessions:
                # If stopped, just clean up without sending end message
                stopped_sessions.remove(session_id)
                print(f"[LLM] Session {session_id} → Stopped.")
            else:
                # Always send llm_end and store the text, even if the stream was interrupted
                await redis.set(f"session:{session_id}:text", full_response)
                await redis.publish(f"session:{session_id}:out", json.dumps({"type": "llm_end", "persona": persona}))
                print(f"[LLM] Session {session_id} → Finished.")


async def control_worker_loop():
    """Listens for control messages like 'stop'."""
    pubsub = redis.pubsub()
    await pubsub.subscribe("session:control")
    print("🚀 LLM control worker listening for stop signals...")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            data = json.loads(message["data"])
            if data.get("type") == "stop_session":
                session_id = data.get("session_id")
                if session_id:
                    stopped_sessions.add(session_id)
                    print(f"[LLM] 🛑 Queued stop for session {session_id}")
        except (json.JSONDecodeError, AttributeError):
            continue


@app.on_event("startup")
async def startup():
    asyncio.create_task(llm_worker_loop())
    asyncio.create_task(control_worker_loop())

# docker compose exec ollama ollama pull tinyllama
