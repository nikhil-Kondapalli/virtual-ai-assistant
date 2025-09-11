# """
# FastAPI TTS Worker - Handles text-to-speech requests via pyttsx3.
# """

import os
import json
import asyncio
import base64
import re
import io
import soundfile as sf
from TTS.api import TTS
import redis.asyncio as aioredis
from fastapi import FastAPI

# --- Configuration ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = FastAPI()
# Load TTS model once
print("🔊 Loading TTS model: tts_models/en/ljspeech/glow-tts")
tts = TTS("tts_models/en/ljspeech/glow-tts")


# --- State Management ---
session_states = {}  # In-memory store for session-specific data


def get_session_state(session_id):
    """Get or create a state for a session."""
    if session_id not in session_states:
        session_states[session_id] = {
            "text_buffer": "",
            "tts_chunks_sent": 0,
        }
    return session_states[session_id]


def cleanup_session_state(session_id):
    """Remove state for a completed or disconnected session."""
    if session_id in session_states:
        del session_states[session_id]


async def tts_worker_loop():
    redis = aioredis.from_url(REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.psubscribe("session:*:out")
    print("🚀 TTS worker started, subscribing to Redis…")

    async for message in pubsub.listen():
        if message["type"] != "pmessage":
            continue

        channel = message["channel"].decode()
        session_id = channel.split(":")[1]

        try:
            data = json.loads(message["data"])
            msg_type = data.get("type")
        except (json.JSONDecodeError, AttributeError):
            continue

        state = get_session_state(session_id)

        if msg_type == "llm_token":
            token = data.get("token", "")
            state["text_buffer"] += token

            # Use regex to find complete sentences (ending with . ! ?)
            sentence_pattern = r"([^.!?]+[.!?])"
            sentences = re.findall(sentence_pattern, state["text_buffer"])

            if sentences:
                text_to_process = "".join(sentences)
                # Update buffer to keep only the partial sentence
                state["text_buffer"] = state["text_buffer"][len(
                    text_to_process):]

                # Generate audio for the complete sentences
                print(
                    f"🗣️ Generating TTS for session {session_id}: '{text_to_process.strip()}'")
                wav = tts.tts(text=text_to_process.strip())

                # Encode and publish the audio chunk
                buf = io.BytesIO()
                sf.write(buf, wav, samplerate=22050, format="WAV")
                b64_chunk = base64.b64encode(buf.getvalue()).decode("utf-8")

                await redis.publish(
                    f"session:{session_id}:out",
                    json.dumps({
                        "type": "tts_chunk",
                        "seq": state["tts_chunks_sent"],
                        "format": "wav",
                        "data": b64_chunk
                    })
                )
                state["tts_chunks_sent"] += 1

        elif msg_type == "llm_end":
            # Process any remaining text in the buffer
            remaining_text = state["text_buffer"].strip()
            if remaining_text:
                print(
                    f"🗣️ Generating TTS for remaining text: '{remaining_text}'")
                wav = tts.tts(text=remaining_text)
                buf = io.BytesIO()
                sf.write(buf, wav, samplerate=22050, format="WAV")
                b64_chunk = base64.b64encode(buf.getvalue()).decode("utf-8")
                await redis.publish(
                    f"session:{session_id}:out",
                    json.dumps(
                        {"type": "tts_chunk", "seq": state["tts_chunks_sent"], "format": "wav", "data": b64_chunk})
                )
                state["tts_chunks_sent"] += 1

            # Send the final end marker and clean up
            await redis.publish(f"session:{session_id}:out", json.dumps({"type": "tts_end", "total_chunks": state["tts_chunks_sent"]}))
            print(f"✅ TTS finished for session {session_id}")
            cleanup_session_state(session_id)


async def control_worker_loop():
    """Listens for control messages like 'stop'."""
    redis = aioredis.from_url(REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.subscribe("session:control")
    print("🚀 TTS control worker listening for stop signals...")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            data = json.loads(message["data"])
            if data.get("type") == "stop_session":
                session_id = data.get("session_id")
                if session_id:
                    print(
                        f"🛑 Clearing TTS state for stopped session {session_id}")
                    cleanup_session_state(session_id)
                    # Also send a tts_end to ensure the client audio queue stops
                    await redis.publish(f"session:{session_id}:out", json.dumps({"type": "tts_end", "total_chunks": 0}))
        except (json.JSONDecodeError, AttributeError):
            continue


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tts_worker_loop())
    asyncio.create_task(control_worker_loop())
