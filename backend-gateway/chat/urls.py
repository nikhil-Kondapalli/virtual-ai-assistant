"""
URL configuration for chat app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.SessionListCreateView.as_view(), name='session-list'),
    path('sessions/<str:session_id>/', views.SessionDetailView.as_view(), name='session-detail'),
    path('sessions/<str:session_id>/messages/', views.MessageListView.as_view(), name='message-list'),
]
