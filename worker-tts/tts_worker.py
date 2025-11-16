# """
# FastAPI TTS Worker - Handles text-to-speech requests via Coqui TTS.
# """

import os
import json
import asyncio
import base64
import io
import soundfile as sf
from TTS.api import TTS
import redis.asyncio as aioredis
from fastapi import FastAPI

# --- Configuration ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = FastAPI()
# Load TTS model once
# Using a faster model suitable for CPU
TTS_MODEL = os.getenv("TTS_MODEL", "tts_models/en/ljspeech/speedy-speech")
print(f"🔊 Loading TTS model: {TTS_MODEL}")
# Make sure to have a GPU-enabled build of PyTorch if you want to use GPU
tts = TTS(TTS_MODEL, gpu=False)


# --- State Management ---
session_states = {}  # In-memory store for session-specific data
stopped_sessions = set()  # Track stopped sessions


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
            # Check if this session was stopped
            if session_id in stopped_sessions:
                print(f"🛑 TTS skipping token for stopped session {session_id}")
                continue

            token = data.get("token", "")
            state["text_buffer"] += token

            delimiters = {'.', '!', '?', ','}
            WORD_COUNT_THRESHOLD = 12

            while True:
                if session_id in stopped_sessions:
                    print(f"🛑 TTS breaking out of sentence loop for stopped session {session_id}")
                    break

                text_buffer = state["text_buffer"]

                # Find the first delimiter
                first_delimiter_pos = -1
                for i, char in enumerate(text_buffer):
                    if char in delimiters:
                        first_delimiter_pos = i
                        break

                text_to_process = None

                if first_delimiter_pos != -1:
                    # Delimiter found, process the chunk up to it
                    text_to_process = text_buffer[:first_delimiter_pos + 1]
                    state["text_buffer"] = text_buffer[first_delimiter_pos + 1:]
                else:
                    # No delimiter, check for word count fallback
                    words = text_buffer.split()
                    if len(words) > WORD_COUNT_THRESHOLD:
                        text_to_process = text_buffer
                        state["text_buffer"] = ""  # Clear buffer

                if text_to_process:
                    print(
                        f"🗣️ Generating TTS for session {session_id}: '{text_to_process.strip()}'")
                    # Run blocking TTS call in a separate thread
                    wav = await asyncio.to_thread(tts.tts, text=text_to_process.strip())

                    # Encode and publish the audio chunk as Ogg/Opus
                    buf = io.BytesIO()
                    sf.write(buf, wav, samplerate=24000,
                             format='OGG', subtype='OPUS')
                    b64_chunk = base64.b64encode(
                        buf.getvalue()).decode("utf-8")

                    await redis.publish(
                        f"session:{session_id}:out",
                        json.dumps({
                            "type": "tts_chunk",
                            "seq": state["tts_chunks_sent"],
                            "format": "opus",
                            "data": b64_chunk
                        })
                    )
                    state["tts_chunks_sent"] += 1
                else:
                    # Nothing to process, break the loop
                    break

        elif msg_type == "llm_end":
            # Check if this session was stopped before processing remaining text
            if session_id in stopped_sessions:
                print(
                    f"🛑 TTS skipping remaining text for stopped session {session_id}")
                cleanup_session_state(session_id)
                continue


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
                    stopped_sessions.add(session_id)
                    cleanup_session_state(session_id)
                    # Also send a tts_end to ensure the client audio queue stops
                    await redis.publish(f"session:{session_id}:out", json.dumps({"type": "tts_end", "total_chunks": 0}))
        except (json.JSONDecodeError, AttributeError):
            continue


@app.on_event("startup")
async def startup_event():
    app.state.tts_task = asyncio.create_task(tts_worker_loop())
    app.state.control_task = asyncio.create_task(control_worker_loop())

@app.on_event("shutdown")
async def shutdown_event():
    print("🔌 Closing TTS worker connections...")
    if hasattr(app.state, "tts_task"):
        app.state.tts_task.cancel()
    if hasattr(app.state, "control_task"):
        app.state.control_task.cancel()
    # await redis.close() # This will be handled by the main worker loop
