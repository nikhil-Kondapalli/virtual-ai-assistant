from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets, generics
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, UserSerializer, GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    ViewSet for viewing and editing user instances.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    ViewSet for viewing and editing group instances.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class SessionListCreateView(generics.ListCreateAPIView):
    """List and create chat sessions."""
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a chat session."""
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


class MessageListView(generics.ListAPIView):
    """List messages for a specific session."""
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=self.request.user
        )
        return ChatMessage.objects.filter(session=session)
