import json
import datetime
from django.db.models import Max
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone, dateformat

from .models import AuctionListing, Comment, User, Bid, Category, Chat, Message


class ListingConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['listing_id']
        self.room_group_name = 'market_%s' % self.room_name
        #Join room group by listing url
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
            )
        self.accept()


    def disconnect(self, close_code):
        #Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
                )
    def new_comment(self, comment_text, listing):
        comment_text = comment_text.strip()
        if comment_text:
            date = timezone.localtime()
            comment = Comment.objects.create(listing = listing, user = self.user, date = date, text = comment_text)
            comment.save()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'post_new_comment',
                    'comment': f"{comment.text}",
                    'username': f"{comment.user.username}",
                    'comment_date':f'{dateformat.format(comment.date, "M d, h:i a")}'
                }
            )       

    #Receive message from WebSocket
    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        try:
            listing = AuctionListing.objects.get(pk = int(text_data_json['listing_id']))
        except KeyError:
            return redirect('market:index')
        else:
            pass

        try:
            comment_text = text_data_json['post_comment']
        except KeyError:
            print("No post_comment")
        else:
            print("letsgo")
            self.new_comment(comment_text, listing)

        try:
            new_bid = float(text_data_json['newbid'])
        except (KeyError, AuctionListing.DoesNotExist, ValueError):
            pass
        else:
            if listing.user == self.user:
                pass
            else:
                bids = Bid.objects.filter(listing=listing)
                date = timezone.now()
                max_value = bids.aggregate(Max('value'))['value__max']
                if max_value is None:
                    max_value = 0
                if new_bid > max_value and new_bid > float(listing.startBid):
                    new_bid_object = Bid.objects.create(value=float(new_bid), user = self.user, listing=listing, date = date)
                    new_bid_object.save()

                    # Send message to room group
                    async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'new_bid_set': f"{new_bid_object.value}"
            }
        )
                else:
                    pass
    
    def chat_message(self, event):
        new_bid_set = event['new_bid_set']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'new_bid_set': new_bid_set,
        }))

    def post_new_comment(self, event):
        comment = event['comment']
        username = event['username']
        comment_date = event['comment_date']

        #Send message to WebSocket
        self.send(text_data = json.dumps({
            'comment':comment,
            'username':username,
            'comment_date':comment_date,
                }))
