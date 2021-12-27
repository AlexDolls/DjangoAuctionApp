from django.urls import reverse
from django.db.models import Max, Sum
from django.utils import timezone, dateformat
from django.shortcuts import redirect

from asgiref.sync import async_to_sync

from channels.generic.websocket import WebsocketConsumer

from .models import AuctionListing, Comment, User, Bid, Category, Chat, Message

import datetime
import json


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

    def end_listing(self, listing):
        if self.user == listing.user:
            listing.active = False
            listing.save()
            """Define winner"""
            bids = Bid.objects.filter(listing=listing)
            if not bids: 
                async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
                {
                'type': 'listing_winner',
                'win_user_id': f"{listing.user.id}"
                }
            )
            else:
                last_bid = bids.order_by('-value')[0]
                win_user = last_bid.user
                win_user.winlist.add(listing)
                new_message_text = f"Hi, you won my listing at link http://127.0.0.1:8000{reverse('market:details', kwargs = {'listing_id':listing.id})}"
                try:
                    chat = Chat.objects.filter(members = win_user).get(members = listing.user)
                except Chat.DoesNotExist:
                    chat = Chat.objects.create()
                    chat.members.add(win_user, listing.user)

                new_message = Message.objects.create(chat=chat, sender_id = listing.user.id, text = new_message_text)
            
                async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
                {
                'type': 'listing_winner',
                'win_user_id': f"{win_user.id}"
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
            endlisting  = text_data_json['endlisting']
        except KeyError:
            pass
        else:
            self.end_listing(listing)

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
                'type': 'new_bid_listing',
                'new_bid_set': f"{new_bid_object.value}"
            }
        )
                else:
                    pass
    
    def new_bid_listing(self, event):
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

    def listing_winner(self,event):
        win_user_id = event['win_user_id']

        #Send message to WebSocket
        self.send(text_data = json.dumps({
            'win_user_id':win_user_id,
            }))

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("HELLO")
        self.user = self.scope['user']
        self.room_group_name = f'chat_{self.user.id}'
        print(f"{self.room_group_name} --- {self.user.username} --- {self.user.id}")

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def new_message_chat_exist(self, chat, sender, message_text):
        date = timezone.localtime()
        message_text = message_text.strip()
        if message_text and len(message_text)<=300:
            message = Message.objects.create(text = message_text, sender_id = sender.id, chat = chat, date = date)
            message.save()
            chat_members = chat.members.all()
            receiver = chat.members.exclude(id=sender.id).first()
            unread_messages_all = 0
            
            for chat_item in Chat.objects.filter(members=receiver):
                for message_item in chat_item.message_set.filter(sender_id = sender.id):
                    if message_item.unread: #BooleanField 'unread' in Message
                        unread_messages_all += 1

            receiver.inbox = unread_messages_all
            receiver.save()

            async_to_sync(self.channel_layer.group_send)(
                f'chat_{receiver.id}',
                {
                    'type': 'chat_message',
                    'message': message.text,
                    'user_inbox': receiver.inbox,
                    'message_date':f'{dateformat.format(message.date, "M d, h:i a")}'
                }
            )
            self.send(text_data = json.dumps(
                    {
                        'message':message.text,
                        'message_date':f'{dateformat.format(message.date, "M d, h:i a")}',
                        'send_self':'yes',
                        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['new_chat']:
            pass
        else:
            try:
                chat = Chat.objects.get(pk = int(text_data_json['chat_id']))
                message_text = text_data_json['new_message_text']
                sender = User.objects.get(pk = int(text_data_json['sender_id']))
            except (KeyError, Chat.DoesNotExist, User.DoesNotExist):
                pass
            else:
                self.new_message_chat_exist(chat, sender, message_text)


    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        user_inbox = event['user_inbox']
        message_date = event['message_date']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'user_inbox': user_inbox,
            'message_date':message_date,
        }))
