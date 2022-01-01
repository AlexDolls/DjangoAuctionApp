from django.urls import reverse
from django.db.models import Max, Sum
from django.utils import timezone, dateformat
from django.shortcuts import redirect

from asgiref.sync import async_to_sync

from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.auth import login, get_user

from .models import AuctionListing, Comment, User, Bid, Category, Chat, Message

import datetime
import json

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"
        


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
        try:
            comment_text = comment_text.strip()
        except AttributeError:
            self.send(text_data=json.dumps({
        'error-socket': "Wrong data type. Only string values for New Comment allowed",
                }))
        else:
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
            else:
                self.send(text_data=json.dumps({
            'error-socket': "New comment text can't be empty string",
                    }))

    def end_listing(self, listing):
        if self.user == listing.user:
            listing.active = False
            listing.save()
            #Define winner
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
        else:
            self.send(text_data=json.dumps({
        'error-socket': "Only listing's owner can end the listing",
                }))

    def new_bid_placement(self, listing, new_bid): 
        if listing.user == self.user:
            self.send(text_data=json.dumps({
        'error-socket': "You can't do bids on own listing.",
                }))
        else:
            try:
                new_bid = float(new_bid)
            except ValueError:
                self.send(text_data=json.dumps({
                        'error-socket':"Non-numeric new-bid value or does not exist.",
                                }))
            else:
                new_bid = float(toFixed(new_bid, 2))
                bids = Bid.objects.filter(listing=listing)
                date = timezone.now()
                max_value = bids.aggregate(Max('value'))['value__max']
                if max_value is None:
                    max_value = 0
                if new_bid > max_value and new_bid > float(listing.startBid) and new_bid <= 99999.99:
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
                    self.send(text_data=json.dumps({
            'error-socket':"Wrong new-bid value.",
                    }))

    #Receive message from WebSocket
    def receive(self, text_data):
        task_checker = False
        if self.user.is_active == True and self.user.is_anonymous == False:
            text_data_json = json.loads(text_data)
            try:
                listing = AuctionListing.objects.get(pk = int(text_data_json['listing_id']))
            except (KeyError, AuctionListing.DoesNotExist):
                self.send(text_data=json.dumps({
                'error-socket': "Can't find the asked listing object.",
                        }))
            if listing.active:
                try:
                    comment_text = text_data_json['post_comment']
                except KeyError:
                    pass
                else:
                    task_checker = True
                    self.new_comment(comment_text, listing)

                try:
                    endlisting  = text_data_json['endlisting']
                except KeyError:
                    pass
                else:
                    task_checker = True
                    self.end_listing(listing)

                try:
                    new_bid = text_data_json['newbid']
                except KeyError:
                    pass
                else:
                    task_checker = True
                    self.new_bid_placement(listing, new_bid)
                if not task_checker:
                    self.send(text_data=json.dumps({
                    'error-socket':"No tasks to do was given",
                            }))
            else:
                self.send(text_data=json.dumps({
                    'error-socket':"Listing is not active. You can't do anything.",
                            }))
        else:
            self.send(text_data=json.dumps({
                    'error-socket':"You must be logged in to make some actions.",
                            }))
    
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
        self.user = self.scope['user']
        if self.user.is_active == True and self.user.is_anonymous == False:
            self.room_group_name = f'chat_{self.user.id}'
            print(f"{self.room_group_name} --- {self.user.username} --- {self.user.id}")

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()
        else:
            self.close()
 
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def new_message_chat_exist(self, chat, message_text):
        date = timezone.localtime()
        try:
            message_text = message_text.strip()
        except (AttributeError, ValueError):
            self.send(text_data = json.dumps(
                        {
                            'error-socket':"Message text must be string value",
                            }))
        else:
            if message_text and len(message_text)<=300:
                sender = User.objects.get(username=f"{self.user}")
                chat_members = chat.members.all()
                if sender in chat.members.all():
                    receiver = chat.members.exclude(id=sender.id).first()
                    if receiver:
                        message = Message.objects.create(text = message_text, sender_id = sender.id, chat = chat, date = date)
                        message.save()
                        unread_messages_all = 0
        # This is exhaustive recount i think
        #            for chat_item in Chat.objects.filter(members=receiver):
        #                for message_item in chat_item.message_set.filter(sender_id = sender.id):
        #                    if message_item.unread: #BooleanField 'unread' in Message
        #                        unread_messages_all += 1
                        for message_item in chat.message_set.filter(sender_id = sender.id):
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
                    else:
                        self.send(text_data = json.dumps(
                            {
                                'error-socket':"You're single user in the chat, can't send message",
                                }))
                else:
                    self.send(text_data = json.dumps(
                            {
                                'error-socket':"Sender is not member of the chat. Can't send the message",
                                }))

            else:
                self.send(text_data = json.dumps(
                        {
                            'error-socket':"The message text can't be empty string",
                            }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        try:
            chat = Chat.objects.get(pk = int(text_data_json['chat_id']))
            message_text = text_data_json['new_message_text']
        except (KeyError, Chat.DoesNotExist):
            self.send(text_data = json.dumps(
                        {
                            'error-socket':"The message requires correct 'chat_id' and 'new_message_text' values",
                            }))
        else:
            self.new_message_chat_exist(chat, message_text)


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
