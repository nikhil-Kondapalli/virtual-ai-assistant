"""
REST API views for chat application.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer


class SessionListCreateView(generics.ListCreateAPIView):
    """List and create chat sessions."""
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a chat session."""
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


class MessageListView(generics.ListAPIView):
    """List messages for a specific session."""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.kwargs['session_id']
        session = get_object_or_404(
            ChatSession, 
            id=session_id, 
            user=self.request.user
        )
        return ChatMessage.objects.filter(session=session)
