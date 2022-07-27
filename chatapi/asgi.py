import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from api.ws_urls import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapi.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    )
})
