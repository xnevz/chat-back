# chat/routing.py
from django.urls import re_path

from .websocket import chat

websocket_urlpatterns = [
    re_path(r'api/chat/ws/$', chat.ChatConsumer.as_asgi()),
]
