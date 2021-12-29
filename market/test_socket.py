import datetime
import pytest

from django.test import TestCase
from django.test import Client
from django.utils import timezone
from django.urls import reverse
from django.conf.urls import url
from django.core.asgi import get_asgi_application

from channels.testing import WebsocketCommunicator
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.db import database_sync_to_async

from .consumers import ListingConsumer, ChatConsumer
from .models import User, Category, AuctionListing, Bid, Comment, Chat, Message

@database_sync_to_async
def async_create_user(username, password):
    user = User.objects.create(username = username)
    user.set_password(password)
    user.save()
    return user

@database_sync_to_async
def async_create_listing(name, image, description, category, user, startBid, days, active):
    """
    Create Listing with given "name", "image", "description", "category", "user", "startBid", "days", "active".
    The start date of listing is timezone.now() and end date is start date + offset by "days" value.
    """
    start_date = timezone.now()
    end_date = start_date + datetime.timedelta(days)
    return AuctionListing.objects.create(name = name, image = image, description = description, category = category, user = user, startBid = startBid, creationDate = start_date, endDate = end_date, active = active)

@database_sync_to_async
def async_create_category(name):
    """
    Create category with given "name".
    """
    return Category.objects.create(name = name)

@database_sync_to_async
def async_login_client(client, username, password):
    client.login(username = username, password = password)
    return client

@database_sync_to_async
def clear_all_bd(*client):
    AuctionListing.objects.all().delete()
    User.objects.all().delete()
    Category.objects.all().delete()
    Bid.objects.all().delete()
    if client:
        del client

"""
ACTIVE LISTING - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_new_bid_placement():
    """
    If given right value for new listing's bid, return new bid value from websocket
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
}) 
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {'new_bid_set': '200.0'}
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_new_bid_placement_wrong_value():
    """
    If given wrong value of new bid (less than startBid value for listing), return Error message from websocket
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
}) 
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"50", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'error-socket':"Wrong new-bid value.",
                    }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_new_bid_placement_non_numeric():
    """
    If given non-numeric value of new bid, return Error message from websocket
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
}) 
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"qwerty", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Non-numeric new-bid value or does not exist.",
                        } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_decimal_value_new_bid_placement():
    """
    If given right decimal value for new listing's bid, return new bid value from websocket with decimal_places = 2 (symbols after coma)
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200.2220", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {'new_bid_set': '200.22'}
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
ACTIVE LISTING - OWNER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_new_bid_placement_owner():
    """
    If right value for listing's new bid given by owner user of listing - return appropriate Error message from websocket that owner can't do bids.
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
}) 
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket': "You can't do bids on own listing.",
                        } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_wrong_value_new_bid_placement_owner():
    """
    If wrong value for listing's new bid given by owner user of listing - return appropriate Error message from websocket that owner can't do bids.
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"50", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket': "You can't do bids on own listing.",
                        }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_non_numeric_new_bid_placement_owner():
    """
    If non numeric value for listing's new bid given by owner user of listing - return appropriate Error message from websocket that owner can't do bids.
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"qwerty", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "You can't do bids on own listing.",
                } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_decimal_value_new_bid_placement_owner():
    """
    If right decimal value for listing's new bid given by owner user of listing - return appropriate Error message from websocket that owner can't do bids.
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200.2220", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket': "You can't do bids on own listing.",
                        }
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
ACTIVE LISTING - ANONYMOUS
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_new_bid_placement_anonymous():
    """
    If given right value for new listing's bid by anonymous user, return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_wrong_value_new_bid_placement_anonymous():
    """
    If given wrong value for new listing's bid by anonymous user, return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"50", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_non_numeric_new_bid_placement_anonymous():
    """
    If given non-numeric value for new listing's bid by anonymous user, return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"qwerty", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_decimal_value_new_bid_placement_anonymous():
    """
    If given right decimal value for new listing's bid by anonymous user, return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200.2220", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()


"""
NOT ACTIVE LISTING - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_new_bid():
    """
    If given right value new bid for non-active listing - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
}) 
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_wrong_value_new_bid():
    """
    If given wrong value new bid for non-active listing - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"50", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_non_numeric_value_new_bid():
    """
    If given non-numeric value new bid for non-active listing - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"qwerty", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_decimal_value_new_bid():
    """
    If given decimal value new bid for non-active listing - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200.2220", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        }
    await communicator.disconnect()
    await clear_all_bd(client_login)


"""
NOT ACTIVE LISTING - OWNER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_new_bid_owner():
    """
    If given right value new bid for non-active listing by owner - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_wrong_value_new_bid_owner():
    """
    If given wrong value new bid for non-active listing by owner - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"50", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_wrong_value_new_bid_owner():
    """
    If given wrong value new bid for non-active listing by owner - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"50", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_non_numeric_value_new_bid_owner():
    """
    If given non-numeric value new bid for non-active listing by owner - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"qwerty", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_not_active_decimal_value_new_bid_owner():
    """
    If right decimal value new bid for non-active listing by owner - return Error message from websocket that listing is Not Active
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200.2220", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                'error-socket':"Listing is not active. You can't do anything.",
                        }
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
NOT ACTIVE LISTING - ANONYMOUS
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_new_bid_placement_anonymous():
    """
    If given right value for new non-active listing's bid by anonymous user, return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_wrong_value_new_bid_placement_anonymous():
    """
    If given wrong value for new non-active listing's bid by anonymous user, return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"50", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_non_numeric_value_new_bid_placement_anonymous():
    """
    If non-numeric value for new non-active listing's bid by anonymous user, return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"qwerty", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_decimal_value_new_bid_placement_anonymous():
    """
    If given right decimal value for new non-active listing's bid by anonymous user, return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    url((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"newbid":"200.2220", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

