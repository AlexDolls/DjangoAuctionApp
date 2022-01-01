import datetime
import pytest

from django.test import Client
from django.utils import timezone
from django.urls import reverse
from django.urls import re_path
from django.core.asgi import get_asgi_application

from channels.testing import WebsocketCommunicator
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.db import database_sync_to_async

from .consumers import ListingConsumer, ChatConsumer
from .models import User, Category, AuctionListing, Bid, Comment, Chat, Message


@database_sync_to_async
def async_create_chat_object(*members):
    chat = Chat.objects.create()
    if members:
        for member in members:
            chat.members.add(member)
        chat.save()
    return chat

@database_sync_to_async
def async_create_bid_object(value, listing, user):
    bid = Bid.objects.create(user = user, listing = listing, value = value, date = timezone.now())
    bid.save()
    return bid


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
def clear_all_bd(*clients):
    AuctionListing.objects.all().delete()
    User.objects.all().delete()
    Category.objects.all().delete()
    Chat.objects.all().delete()
    if clients:
        for client in clients:
            del client

#WebSocket ListingConsumer tests
#New Bid Placement
"""
NEW BID ACTIVE LISTING - LOGGED USER
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
NEW BID ACTIVE LISTING - OWNER
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
NEW BID ACTIVE LISTING - ANONYMOUS
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
NEW BID NOT ACTIVE LISTING - LOGGED USER
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
NEW BID NOT ACTIVE LISTING - OWNER
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
NEW BID NOT ACTIVE LISTING - ANONYMOUS
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
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

#End Listing
"""
END LISTING ACTIVE LISTING - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing():
    """
    If logged in user trying to end active listing, return Error from websocket that non-owner can't stop the listing
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "Only listing's owner can end the listing",
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_value():
    """
    If logged in user trying to end active listing by giving numeric value in key 'endlisting', return Error from websocket that non-owner can't stop the listing
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "Only listing's owner can end the listing",
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_bid_exist():
    """
    If logged in user trying to end active listing and of another user exist, return Error from websocket that non-owner can't stop the listing
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    user_bid = await async_create_user(username = "test_bid_user", password = "test_bid_user")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid = await async_create_bid_object(user = user_bid, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "Only listing's owner can end the listing",
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_bid_exist():
    """
    If logged in user trying to end active listing and gives numeric value in "endlisting" message key, bid of another user exists, return Error from websocket that non-owner can't stop the listing
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    user_bid = await async_create_user(username = "test_bid_user", password = "test_bid_user")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid = await async_create_bid_object(user = user_bid, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "Only listing's owner can end the listing",
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
END LISTING ACTIVE LISTING - OWNER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_owner_no_bids():
    """
    If listing's owner trying to end active listing without bids, return message from websocket that owner is listing's winner
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'win_user_id':f"{user.id}",
            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_owner_no_bids():
    """
    If listing's owner trying to end active listing without bids and gives numeric data in "endlisting" message key, return message from websocket that owner is listing's winner
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'win_user_id':f"{user.id}",
            }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_owner_bid_exist():
    """
    If listing's owner trying to end active listing with bid, return message from websocket that bid maker is listing's winner
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_winner = await async_create_user(username = "user_winner", password = "user_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid_user_winner = await async_create_bid_object(user = user_winner, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'win_user_id':f"{user_winner.id}",
            }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_owner_bid_exist():
    """
    If listing's owner trying to end active listing with bid and gives numeric value in "endlisting" message key, return message from websocket that bid maker is listing's winner
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_winner = await async_create_user(username = "user_winner", password = "user_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid_user_winner = await async_create_bid_object(user = user_winner, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'win_user_id':f"{user_winner.id}",
            }
    await communicator.disconnect()
    await clear_all_bd(client_login)


"""
END LISTING ACTIVE LISTING - ANONYMOUS USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_anonymous():
    """
    If anonymous trying to end active listing, return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_anonymous():
    """
    If anonymous trying to end active listing and gives numeric value to "endlisting" message key, return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_anonymous_bid_exist():
    """
    If anonymous trying to end active listing and another user bid exists - return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    user_bid = await async_create_user(username = "test_user_bid", password = "test_user_password")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid = await async_create_bid_object(value = 200, listing = listing, user = user_bid)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_anonymous_bid_exist():
    """
    If anonymous trying to end active listing and gives numeric value in "endlisting" message key, another user bid exists - return Error from websocket that user need to be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    user_bid = await async_create_user(username = "test_user_bid", password = "test_user_password")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid = await async_create_bid_object(value = 200, listing = listing, user = user_bid)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

"""
END LISTING ACTIVE LISTING - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing():
    """
    If logged in user trying to end active listing, return Error from websocket that non-owner can't stop the listing
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "Only listing's owner can end the listing",
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_value():
    """
    If logged in user trying to end active listing by giving numeric value in key 'endlisting', return Error from websocket that non-owner can't stop the listing
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "Only listing's owner can end the listing",
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_bid_exist():
    """
    If logged in user trying to end active listing and of another user exist, return Error from websocket that non-owner can't stop the listing
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    user_bid = await async_create_user(username = "test_bid_user", password = "test_bid_user")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid = await async_create_bid_object(user = user_bid, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "Only listing's owner can end the listing",
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_bid_exist():
    """
    If logged in user trying to end active listing and gives numeric value in "endlisting" message key, bid of another user exists, return Error from websocket that non-owner can't stop the listing
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    user_bid = await async_create_user(username = "test_bid_user", password = "test_bid_user")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid = await async_create_bid_object(user = user_bid, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "Only listing's owner can end the listing",
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
END LISTING ACTIVE LISTING - OWNER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_owner_no_bids():
    """
    If listing's owner trying to end active listing without bids, return message from websocket that owner is listing's winner
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'win_user_id':f"{user.id}",
            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_owner_no_bids():
    """
    If listing's owner trying to end active listing without bids and gives numeric data in "endlisting" message key, return message from websocket that owner is listing's winner
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'win_user_id':f"{user.id}",
            }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_owner_bid_exist():
    """
    If listing's owner trying to end active listing with bid, return message from websocket that bid maker is listing's winner
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_winner = await async_create_user(username = "user_winner", password = "user_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid_user_winner = await async_create_bid_object(user = user_winner, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'win_user_id':f"{user_winner.id}",
            }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_owner_bid_exist():
    """
    If listing's owner trying to end active listing with bid and gives numeric value in "endlisting" message key, return message from websocket that bid maker is listing's winner
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_winner = await async_create_user(username = "user_winner", password = "user_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid_user_winner = await async_create_bid_object(user = user_winner, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'win_user_id':f"{user_winner.id}",
            }
    await communicator.disconnect()
    await clear_all_bd(client_login)


"""
END LISTING ACTIVE LISTING - ANONYMOUS USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_anonymous():
    """
    If anonymous trying to end active listing, return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_anonymous():
    """
    If anonymous trying to end active listing and gives numeric value to "endlisting" message key, return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_anonymous_bid_exist():
    """
    If anonymous trying to end active listing and another user bid exists - return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    user_bid = await async_create_user(username = "test_user_bid", password = "test_user_password")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid = await async_create_bid_object(value = 200, listing = listing, user = user_bid)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_anonymous_bid_exist():
    """
    If anonymous trying to end active listing and gives numeric value in "endlisting" message key, another user bid exists - return Error from websocket that user need to be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    user_bid = await async_create_user(username = "test_user_bid", password = "test_user_password")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    new_bid = await async_create_bid_object(value = 200, listing = listing, user = user_bid)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

#End listing - Not Active Listing
"""
END LISTING NOT ACTIVE LISTING - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing():
    """
    If logged in user trying to end not active listing, return Error from websocket that can't do actoins with non-active listing
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_value():
    """
    If logged in user trying to end non-active listing by giving numeric value in key 'endlisting', return Error that can't do actions with non-active listing
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_bid_exist():
    """
    If logged in user trying to end non-active listing and of another user exist, return Error from websocket that can't do actions with non-active listing
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    user_bid = await async_create_user(username = "test_bid_user", password = "test_bid_user")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    new_bid = await async_create_bid_object(user = user_bid, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_bid_exist():
    """
    If logged in user trying to end non-active listing and gives numeric value in "endlisting" message key, bid of another user exists, return Error from websocket that can't do actions with non-active listing
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_2 = await async_create_user(username = "test_user_2", password = "test_password")
    user_bid = await async_create_user(username = "test_bid_user", password = "test_bid_user")
    client_login = await async_login_client(client, "test_user_2", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    new_bid = await async_create_bid_object(user = user_bid, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
END LISTING NOT ACTIVE LISTING - OWNER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_owner_no_bids():
    """
    If listing's owner trying to end non-active listing without bids, return message from websocket that can't do actions with non-active listing
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            }
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_owner_no_bids():
    """
    If listing's owner trying to end non-active listing without bids and gives numeric data in "endlisting" message key, return message from websocket that can't do actions with non-active listing
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_owner_bid_exist():
    """
    If listing's owner trying to end non-active listing with bid, return message from websocket that can't do actions with non-active listing
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_winner = await async_create_user(username = "user_winner", password = "user_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    new_bid_user_winner = await async_create_bid_object(user = user_winner, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_owner_bid_exist():
    """
    If listing's owner trying to end non-active listing with bid and gives numeric value in "endlisting" message key, return message from websocket that can't do actions with non-active listing
    """
    client = Client()
    user = await async_create_user(username = "test_user", password = "test_password")
    user_winner = await async_create_user(username = "user_winner", password = "user_password")
    client_login = await async_login_client(client, "test_user", "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    new_bid_user_winner = await async_create_bid_object(user = user_winner, listing = listing, value = 200)
    headers = [(b'origin', b'...'), (b'cookie', client_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)


"""
END LISTING NOT ACTIVE LISTING - ANONYMOUS USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_anonymous():
    """
    If anonymous trying to end non-active listing, return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_anonymous():
    """
    If anonymous trying to end non-active listing and gives numeric value to "endlisting" message key, return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_anonymous_bid_exist():
    """
    If anonymous trying to end non-active listing and another user bid exists - return Error from websocket that user need to be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    user_bid = await async_create_user(username = "test_user_bid", password = "test_user_password")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    new_bid = await async_create_bid_object(value = 200, listing = listing, user = user_bid)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":"end", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_end_listing_numeric_anonymous_bid_exist():
    """
    If anonymous trying to end non-active listing and gives numeric value in "endlisting" message key, another user bid exists - return Error from websocket that user need to be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    user_bid = await async_create_user(username = "test_user_bid", password = "test_user_password")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    new_bid = await async_create_bid_object(value = 200, listing = listing, user = user_bid)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"endlisting":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }
    await communicator.disconnect()
    await clear_all_bd()

#Post new comment on Listing page
"""
POST NEW COMMENT ACTIVE LISTING - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment():
    """
    If given right value for new comment at active listing - return from websocket message with all info for new comment that will be posted.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"new_comment", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'comment':'new_comment',
            'username':f'{user_2.username}',
            'comment_date':response['comment_date'],
                } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_empty():
    """
    If given empty string value for new comment at active listing - return from websocket Error that value for New Comment can't be empty string.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "New comment text can't be empty string",
                } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_whitespaces_only():
    """
    If given only whitespaces in  value for new comment at active listing - return from websocket Error that value for New Comment can't be empty string.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"          ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "New comment text can't be empty string",
                }
 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_whitespaces_from_begin_and_end():
    """
    If given right value for new comment at active listing, but whitespaces placed before and after text - return from websocket message with all info for new comment without extra whitespaces that will be posted.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"     new_comment     ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'comment':'new_comment',
            'username':f'{user_2.username}',
            'comment_date':response['comment_date'],
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_numeric():
    """
    If given numeric value for new comment at active listing - return from websocket Error that data type for New Comment must be string.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'error-socket': "Wrong data type. Only string values for New Comment allowed",
                    } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
POST NEW COMMENT ACTIVE LISTING - OWNER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_owner():
    """
    If given right value for new comment at active listing from listing's owner - return from websocket message with all info for new comment that will be posted.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"new_comment", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'comment':'new_comment',
            'username':f'{user.username}',
            'comment_date':response['comment_date'],
                } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_empty_owner():
    """
    If given empty string value for new comment at active listing from listing's owner - return from websocket Error that value for New Comment can't be empty string.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "New comment text can't be empty string",
                } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_whitespaces_only_owner():
    """
    If given only whitespaces in  value for new comment at active listing from listing's owner - return from websocket Error that value for New Comment can't be empty string.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"          ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket': "New comment text can't be empty string",
                }
 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_whitespaces_from_begin_and_end_owner():
    """
    If given right value for new comment at active listing from listing owner, but whitespaces placed before and after text - delete whitespaces and return new comment info.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"     new_comment     ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'comment':'new_comment',
            'username':f'{user.username}',
            'comment_date':response['comment_date'],
                }
    await communicator.disconnect()
    await clear_all_bd(client_login)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_numeric_owner():
    """
    If given numeric value for new comment at active listing from listing's owner - return from websocket Error that data type for New Comment must be string.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
            'error-socket': "Wrong data type. Only string values for New Comment allowed",
                    } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
POST NEW COMMENT ACTIVE LISTING - ANONYMOUS USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_anonymous():
    """
    Anonymous User
    If given right value for new comment at active listing - return Error from websocket that user must be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"new_comment", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_empty_anonymous():
    """
    Anonymous User
    If given empty string value for new comment at active listing - return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_whitespaces_only_anonymous():
    """
    Anonymous User
    If given only whitespaces in  value for new comment at active listing - return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"          ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_whitespaces_from_begin_and_end_anonymous():
    """
    Anonymous User
    If given right value for new comment at active listing, but whitespaces placed before and after text - return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"     new_comment     ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_listing_post_new_comment_numeric_anonymous():
    """
    Anonymous User
    If given numeric value for new comment at active listing - return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }

    await communicator.disconnect()
    await clear_all_bd()

#Post new comment on Not Active Listing page
"""
POST NEW COMMENT NOT ACTIVE LISTING - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment():
    """
    If given right value for new comment at non-active listing - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"new_comment", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_empty():
    """
    If given empty string value for new comment at non-active listing - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_whitespaces_only():
    """
    If given only whitespaces in  value for new comment at non-active listing - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"          ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_whitespaces_from_begin_and_end():
    """
    If given right value for new comment at non-active listing, but whitespaces placed before and after text - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"     new_comment     ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_numeric():
    """
    If given numeric value for new comment at non-active listing - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
POST NEW COMMENT NOT ACTIVE LISTING - OWNER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_owner():
    """
    If given right value for new comment at non-active listing from listing's owner - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"new_comment", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_empty_owner():
    """
    If given empty string value for new comment at non-active listing from listing's owner - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_whitespaces_only_owner():
    """
    If given only whitespaces in  value for new comment at non-active listing from listing's owner - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"          ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
 
    await communicator.disconnect()
    await clear_all_bd(client_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_whitespaces_from_begin_and_end_owner():
    """
    If given right value for new comment at non-active listing from listing owner, but whitespaces placed before and after text - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"     new_comment     ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_numeric_owner():
    """
    If given numeric value for new comment at non-active listing from listing's owner - return Error from websocket that listing is not active.
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
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}),headers)
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
        'error-socket':"Listing is not active. You can't do anything.",
                            } 
    await communicator.disconnect()
    await clear_all_bd(client_login)

"""
POST NEW COMMENT NOT ACTIVE LISTING - ANONYMOUS USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_anonymous():
    """
    Anonymous User
    If given right value for new comment at non-active listing - return Error from websocket that user must be logged in
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"new_comment", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_empty_anonymous():
    """
    Anonymous User
    If given empty string value for new comment at non-active listing - return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_whitespaces_only_anonymous():
    """
    Anonymous User
    If given only whitespaces in  value for new comment at non-active listing - return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"          ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_whitespaces_from_begin_and_end_anonymous():
    """
    Anonymous User
    If given right value for new comment at non-active listing, but whitespaces placed before and after text - return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":"     new_comment     ", "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            } 
    await communicator.disconnect()
    await clear_all_bd()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_not_active_listing_post_new_comment_numeric_anonymous():
    """
    Anonymous User
    If given numeric value for new comment at non-active listing - return Error from websocket that user must be logged in.
    """
    user = await async_create_user(username = "test_user", password = "test_password")
    category = await async_create_category(name = "test_category")
    listing = await async_create_listing(name = "test_listing", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
                    re_path((r"^ws/market/(?P<listing_id>\w+)/$"),ListingConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:details", kwargs = {"listing_id":listing.id}))
    connected, subprotocol = await communicator.connect()
    assert connected
    await communicator.send_json_to({"post_comment":1, "listing_id":listing.id})
    response = await communicator.receive_json_from()
    assert response == {
                    'error-socket':"You must be logged in to make some actions.",
                            }

    await communicator.disconnect()
    await clear_all_bd()

"""--------------------------ChatConsumer--------------------------"""
#send_message
"""
SEND MESSAGE CHAT EXIST - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist():
    """
    if user sends correct values for new message and chat exist - return from websocket all info about new message
    """
    client_sender = Client()
    client_receiver = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    receiver_login = await async_login_client(client_receiver, "receiver", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    headers_receiver = [(b'origin', b'...'), (b'cookie', receiver_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    receiver_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_receiver)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    connected_receiver, subprotocol_receiver = await receiver_communicator.connect()
    assert connected_sender
    assert connected_receiver
    await sender_communicator.send_json_to({"new_message_text":"Hello World!", "chat_id":chat.id})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                                'message':"Hello World!",
                                'message_date':sender_response['message_date'],
                                'send_self':'yes',
                                }
    receiver_response = await receiver_communicator.receive_json_from()
    assert receiver_response == {
            'message': "Hello World!",
            'user_inbox': 1,
            'message_date':receiver_response["message_date"],
        } 
    await sender_communicator.disconnect()
    await receiver_communicator.disconnect()
    await clear_all_bd(receiver_login, sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist_message_between_whitespaces():
    """
    if user sends correct values for new message and chat exist, but from start and from end whitespaces - return from websocket all info about new message without extra whitespaces
    """
    client_sender = Client()
    client_receiver = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    receiver_login = await async_login_client(client_receiver, "receiver", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    headers_receiver = [(b'origin', b'...'), (b'cookie', receiver_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    receiver_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_receiver)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    connected_receiver, subprotocol_receiver = await receiver_communicator.connect()
    assert connected_sender
    assert connected_receiver
    await sender_communicator.send_json_to({"new_message_text":"          Hello World!         ", "chat_id":chat.id})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                                'message':"Hello World!",
                                'message_date':sender_response['message_date'],
                                'send_self':'yes',
                                }
    receiver_response = await receiver_communicator.receive_json_from()
    assert receiver_response == {
            'message': "Hello World!",
            'user_inbox': 1,
            'message_date':receiver_response["message_date"],
        }
    await sender_communicator.disconnect()
    await receiver_communicator.disconnect()
    await clear_all_bd(receiver_login, sender_login)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist_sender_not_member():
    """
    if user sends correct values for new message and chat exist, but user is not chat's member - return appropriate Error from websocket
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"Hello World!", "chat_id":chat.id})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"Sender is not member of the chat. Can't send the message",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist_no_reciver():
    """
    if user sends correct values for new message and chat exist, but there is no receiver chat member - return appropriate Error from websocket
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    chat = await async_create_chat_object(sender)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"Hello World!", "chat_id":chat.id})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"You're single user in the chat, can't send message",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist_empty_message():
    """
    if user sends empty value for new message and chat exists - return appropriate Error from websocket
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"", "chat_id":chat.id})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message text can't be empty string",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist_whitespaces_only_message():
    """
    if user sends string that includes only whitespaces as value for new message and chat exists - return appropriate Error from websocket that message can't be empty
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"           ", "chat_id":chat.id})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message text can't be empty string",
                            }
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist_numeric_value():
    """
    if user numeric value for new message and chat exists - return appropriate Error from websocket that message can't not string value
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":1, "chat_id":chat.id})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"Message text must be string value",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist_json_message_key_not_exist():
    """
    if user don't send json message key and chat exists - return appropriate Error from websocket
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"chat_id":chat.id})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_exist_json_chat_id_key_not_exist():
    """
    if user don't send json chat_id key and chat exists - return appropriate Error from websocket
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"Hello World!"})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            }
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

"""
SEND MESSAGE CHAT DOES NOT EXIST - LOGGED USER
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist():
    """
    if user sends correct values for new message and chat not exist - return from websocket message that chat does not exist
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"Hello World!", "chat_id":1})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist_message_between_whitespaces():
    """
    if user sends correct values for new message and chat not exist, but from start and from end whitespaces - return from websocket message that chat does not exist 
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"Hello World!", "chat_id":1})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            }
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)




@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist_sender_not_member():
    """
    if user sends correct values for new message and chat not exist, but user is not chat's member - return from websocket message that chat does not exist 

    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"Hello World!", "chat_id":1})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist_no_reciver():
    """
    if user sends correct values for new message and chat not exist, but there is no receiver chat member - return from websocket message that chat does not exist
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    chat = await async_create_chat_object(sender)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"Hello World!", "chat_id":1})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist_empty_message():
    """
    if user sends empty value for new message and chat not exists - return from websocket message that chat does not exist
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"", "chat_id":1})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist_whitespaces_only_message():
    """
    if user sends string that includes only whitespaces as value for new message and chat not exists - return from websocket message that chat does not exist
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"           ", "chat_id":1})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist_numeric_value():
    """
    if user numeric value for new message and chat not exists - return from websocket message that chat does not exist 
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":1, "chat_id":1})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist_json_message_key_not_exist():
    """
    if user don't send json message key and chat not exists - return from websocket message that chat does not exist
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"chat_id":1})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            } 
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_chat_not_exist_json_chat_id_key_not_exist():
    """
    if user don't send json chat_id key and chat not exists - return from websocket message that chat does not exist
    """
    client_sender = Client()
    sender = await async_create_user(username = "sender", password = "test_password")
    receiver = await async_create_user(username = "receiver", password = "test_password")
    chat = await async_create_chat_object(sender, receiver)
    sender_login = await async_login_client(client_sender, "sender", "test_password")
    headers_sender = [(b'origin', b'...'), (b'cookie', sender_login.cookies.output(header='', sep='; ').encode())]
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    sender_communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"), headers_sender)
    connected_sender, subprotocol_sender = await sender_communicator.connect()
    assert connected_sender
    await sender_communicator.send_json_to({"new_message_text":"Hello World!"})
    sender_response = await sender_communicator.receive_json_from()
    assert sender_response == {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            }
    await sender_communicator.disconnect()
    await clear_all_bd(sender_login)

"""
CONNECT TO WEBSOCKET - ANONYMOUS
"""
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_connect_to_chat_websocket_anonymous():
    """
    if anonymous user try to connect to websocket by ChatConsumer - don't allow connection
    """
    application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path((r"^ws/market/inbox/$"),ChatConsumer.as_asgi()),
                    ])
        ),
})
    communicator = WebsocketCommunicator(application, "ws" + reverse("market:inbox"))
    connected, subprotocol = await communicator.connect()
    assert not connected

