import os
from market.consumers import *
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
# from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auctsite.settings')
# django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    # "http": django_asgi_app,

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r"^ws/market/inbox/$", ChatConsumer.as_asgi()),
            re_path(r"^ws/market/(?P<listing_id>\w+)/$", ListingConsumer.as_asgi()),
        ])
    ),
    # Just HTTP for now. (We can add other protocols later.)
})
