# """
# WebSocket consumers for real-time chat with Virtual agent.
# """

import json
import uuid
import redis.asyncio as aioredis
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

REDIS_URL = "redis://redis:6379/0"
redis = aioredis.from_url(REDIS_URL)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Assign unique session_id per websocket
        self.session_id = str(uuid.uuid4())
        self.persona = "kira_v1"  # Default persona
        await self.accept()

        # Start Redis listener in background
        self.listen_task = asyncio.create_task(self.listen_to_redis())

        # Send meta info to frontend
        await self.send(text_data=json.dumps({
            "type": "meta",
            "id": self.session_id,
            "persona": self.persona
        }))
        print(f"✅ WebSocket connected → session {self.session_id}")

    async def disconnect(self, close_code):
        if hasattr(self, "listen_task"):
            self.listen_task.cancel()
        print(f"⚠️ WebSocket disconnected → session {self.session_id}")

    async def receive(self, text_data):
        """Handles messages from frontend"""
        data = json.loads(text_data)
        msg_type = data.get("type")

        if msg_type == "user_message":
            user_msg = data.get("message", "").strip()
            if not user_msg:
                return

            print(f"📝 Session {self.session_id} → {user_msg}")

            # Publish into Redis for workers
            await redis.publish(
                f"session:{self.session_id}:in",
                json.dumps({"prompt": user_msg, "persona": self.persona})
            )

        elif msg_type == "stop_generation":
            print(f"🛑 Session {self.session_id} → Stop request received")
            await redis.publish(
                "session:control",
                json.dumps({"type": "stop_session",
                           "session_id": self.session_id})
            )

    async def listen_to_redis(self):
        """Listen to Redis output for this session"""
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"session:{self.session_id}:out")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            try:
                payload = json.loads(message["data"])
            except Exception:
                continue

            # Forward worker output to frontend
            await self.send(text_data=json.dumps(payload))
