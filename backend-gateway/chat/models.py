from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """Represents a chat session with the Virtual agent."""
    id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    persona = models.CharField(max_length=50, default='kira_v1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    """Stores chat messages for history and analytics."""
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['timestamp']
