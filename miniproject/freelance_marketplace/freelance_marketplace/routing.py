from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import GigGh.routing 
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_marketplace.settings') 

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Regular HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            GigGh.routing.websocket_urlpatterns  
        )
    ),
})