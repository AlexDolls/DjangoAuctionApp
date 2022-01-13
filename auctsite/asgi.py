import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.conf.urls import url

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auctsite.settings')
django_asgi_app = get_asgi_application()

from market.consumers import ListingConsumer, ChatConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    
    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
    # Just HTTP for now. (We can add other protocols later.)
})
