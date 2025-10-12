"""
Serializers for chat models.
"""
from rest_framework import serializers
from .models import ChatSession, ChatMessage
from django.contrib.auth.models import User, Group


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for user model."""

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']
        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'pk'}
        }


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for group model."""

    class Meta:
        model = Group
        fields = ['url', 'name']
        extra_kwargs = {
            'url': {'view_name': 'group-detail', 'lookup_field': 'pk'}
        }


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""

    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'timestamp', 'metadata']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions."""
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'persona', 'created_at',
                  'updated_at', 'is_active', 'messages']
