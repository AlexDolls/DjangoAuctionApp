from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse

from auctsite.celery import app
from .models import *


@app.task
def create_task(listing_id):
    channel_layer = get_channel_layer()
    try:
        listing = AuctionListing.objects.get(id=listing_id)
    except AuctionListing.DoesNotExist:
        return False
    listing.active = False
    listing.save()
    # Define winner
    bids = Bid.objects.filter(listing=listing)
    if not bids:
        async_to_sync(channel_layer.group_send)(
            "market_%s" % listing.id,
            {
                'type': 'listing_winner',
                'win_user_id': f"{listing.user.id}"
            }
        )
    else:
        last_bid = bids.order_by('-value')[0]
        win_user = last_bid.user
        win_user.winlist.add(listing)
        win_user.save()
        new_message_text = f"Hi, you won my listing at link {reverse('market:details', kwargs={'listing_id': listing.id})}"
        try:
            chat = Chat.objects.filter(members=win_user).get(members=listing.user)
        except Chat.DoesNotExist:
            chat = Chat.objects.create()
            chat.members.add(win_user, listing.user)

        new_message = Message.objects.create(chat=chat, sender_id=listing.user.id, text=new_message_text)

        async_to_sync(channel_layer.group_send)(
            "market_%s" % listing.id,
            {
                'type': 'listing_winner',
                'win_user_id': f"{win_user.id}"
            }
        )

        return True
