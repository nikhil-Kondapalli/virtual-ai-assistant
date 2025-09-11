# """
# WebSocket routing for chat application.
# """

# chat/routing.py
from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<str:session_id>/", consumers.ChatConsumer.as_asgi()),
]
