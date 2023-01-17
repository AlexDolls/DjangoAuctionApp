import datetime
import json
import string

from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import UserAvatarForm
from .models import *
from .serializers import BidSerializer
from .tasks import create_task


# Create your views here.

# Checks if given string contains other symnols that allowed
def uses_other_chars(s, given=frozenset(string.ascii_letters + string.digits + '-._')):
    return not set(s) <= given


class GetListingBidsTotalInfoView(APIView):
    @staticmethod
    def get(request, listing_id):
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        bids = Bid.objects.filter(listing=listing)
        if not bids:
            pass
        else:
            all_bids = Bid.objects.filter(listing=listing).order_by('date')
            queryset = all_bids
            serializer_for_queryset = BidSerializer(
                instance=queryset,
                many=True
            )
            return Response(serializer_for_queryset.data)
        return Response(json.dumps({'value': 'No bids yet :)'}))


class GetListingBidInfoView(APIView):
    @staticmethod
    def get(request, listing_id):
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        bids = Bid.objects.filter(listing=listing)
        if not bids:
            pass
        else:
            last_bid = Bid.objects.filter(listing=listing).order_by('-value')[0]
            queryset = last_bid
            serializer_for_queryset = BidSerializer(
                instance=queryset,
                many=False
            )
            return Response(serializer_for_queryset.data)
        return Response(json.dumps({'value': 'No bids yet :)'}))


class IndexView(generic.ListView):
    template_name = 'market/index.html'
    context_object_name = 'active_listing_list'

    def get_queryset(self):
        """Return all listing that exist."""
        return AuctionListing.objects.all()


def details(request, listing_id):
    server_datetime = timezone.now()
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    bids = Bid.objects.filter(listing=listing)
    comments = Comment.objects.filter(listing=listing)
    comments = comments.order_by("date")
    max_value = bids.aggregate(Max('value'))['value__max']
    bid_item = None
    true_user = False

    if max_value is not None:
        bid_item = Bid.objects.filter(value=max_value)[0]
    if listing.user == request.user:
        true_user = True

    min_value = listing.startBid

    if bid_item:
        min_value = float(bid_item.value)
        min_value = round(min_value, 2)
        min_value = min_value + 0.01

    return render(request, "market/detail.html", {
        "server_datetime": server_datetime,
        'true_user': true_user,
        'auctionlisting': listing,
        'bids': bids,
        'comments': comments,
        'bid': bid_item,
        'min_value': min_value,
        'user': request.user
    })


@login_required
def makebid(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)

    if request.user == listing.user:
        messages.warning(request, "Creator of listing can't do bids.")
        return HttpResponseRedirect(reverse("market:details", kwargs={"listing_id": listing.id}))

    else:
        bids = Bid.objects.filter(listing=listing)
        user = request.user
        date = timezone.now()
        max_value = bids.aggregate(Max('value'))['value__max']
        if max_value is None:
            max_value = 0

        try:
            new_bid = request.POST['newbid']
        except KeyError:
            messages.warning(request, "You didn't give any value.")
            return HttpResponseRedirect(reverse("market:details", kwargs={'listing_id': listing.id}))

        else:
            try:
                new_bid = float(new_bid)
            except ValueError:
                messages.warning(request, "You didn't give any value.")
                return HttpResponseRedirect(reverse("market:details", kwargs={'listing_id': listing.id}))
            else:
                new_bid = float(new_bid)
                if new_bid > max_value and new_bid > float(listing.startBid):
                    new_bid_object = Bid.objects.create(value=float(new_bid), user=user, listing=listing, date=date)
                    new_bid_object.save()
                    return HttpResponseRedirect(reverse('market:details', kwargs={'listing_id': listing.id}))
                else:
                    messages.warning(request, "Bid Value must be bigger than Start Price and Last Bid.")
                    return HttpResponseRedirect(reverse("market:details", kwargs={'listing_id': listing.id}))


@login_required
def createListing(request):
    if request.method == "POST":
        user = request.user
        active = True
        current_date = timezone.now()
        try:
            hours = int(request.POST['expiretime'])
            name = f"{request.POST['listingname']}"
            category = request.POST['category']
            startBid = float(request.POST['startBid'])
            description = f"{request.POST['listingdesc']}"
        except (KeyError, ValueError):
            messages.warning(request, "All fields must be filled in, check this out and try again")
            return HttpResponseRedirect(reverse("market:createListing"))

        try:
            image_file = request.FILES.get("loaded-image")
        except(KeyError, ValueError):
            image_file = ""
            pass
        try:
            image = f"{request.POST['imageurl']}"
        except(KeyError, ValueError):
            image = ""
        try:
            category = Category.objects.get(pk=category)
        except(ValueError, KeyError, Category.DoesNotExist):
            messages.warning(request, "You didn't select a category")
            return HttpResponseRedirect(reverse("market:createListing"))
        else:
            if len(name) > 32:
                messages.warning(request, "Name for listing is too long, must be less than 33")
                return HttpResponseRedirect(reverse("market:createListing"))
            elif startBid > 99999.00 or startBid < 0.01:
                messages.warning(request, "Listing Start Price must be bigger than 0.01 and less than 99999.00")
                return HttpResponseRedirect(reverse("market:createListing"))
            elif len(description) > 150:
                messages.warning(request, "Description length must be less than 151")
                return HttpResponseRedirect(reverse("market:createListing"))
            else:
                if not image:
                    image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px" \
                            "-No_image_available.svg.png"
                end_date = current_date + datetime.timedelta(hours=hours)

                new_listing = AuctionListing.objects.create(
                    name=name,
                    description=description,
                    loaded_image=image_file,
                    image=image,
                    category=category,
                    user=user,
                    startBid=startBid,
                    creationDate=current_date,
                    endDate=end_date, active=active
                )

                new_listing.save()
                seconds_to_end = int(datetime.timedelta.total_seconds(new_listing.endDate - new_listing.creationDate))
                task = create_task.apply_async(kwargs={"listing_id": new_listing.id}, countdown=seconds_to_end)
                return HttpResponseRedirect(reverse("market:details", kwargs={"listing_id": new_listing.id}))
    return render(request, "market/createListing.html", {"categories": Category.objects.all()})


@login_required
def editListing(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    if request.method == "POST":
        user = request.user
        if user != listing.user:
            messages.warning(request, "You don't have permission to do this!")
            return HttpResponseRedirect(reverse("market:editListingPage", kwargs={'listing_id': listing.id}))
        else:
            try:
                description = request.POST['listingdesc']
                name = request.POST['listingname']
            except KeyError:
                messages.warning(request, "You didn't give any values")
                return HttpResponseRedirect(reverse("market:editListingPage", kwargs={'listing_id': listing.id}))
            try:
                image_file = request.FILES.get("loaded-image")
            except(KeyError, ValueError):
                image_file = ""
                pass
            try:
                image = f"{request.POST['imageurl']}"
            except(KeyError, ValueError):
                image = ""
                pass
            if not image:
                image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px" \
                        "-No_image_available.svg.png"

            listing.image = image
            listing.loaded_image = image_file
            listing.name = name
            listing.description = description
            listing.save()
            return HttpResponseRedirect(reverse("market:details", kwargs={'listing_id': listing.id}))
    return render(request, "market/editListing.html", {'listing': listing})


def signup(request):
    if request.method == "POST":
        try:
            username = request.POST['username'].strip()
            email = request.POST['email'].strip()
            password = request.POST['password'].strip()
            confirm_password = request.POST['confirm_password'].strip()
        except (ValueError, KeyError, AttributeError):
            messages.warning(request, "You did't fill all fields.")
            return HttpResponseRedirect(reverse('market:signup'))
        else:
            if len(username) == 0 or len(email) == 0:
                messages.warning(request, "All fields must be filled.")
                return HttpResponseRedirect(reverse('market:signup'))
            if (uses_other_chars(username) or uses_other_chars(email, given=frozenset(
                    string.ascii_letters + string.digits + '-._' + '@')) or uses_other_chars(password)):
                messages.warning(request, "Unsupported characters was given in fields. \
                                            Supported symbols: '-_.', letters, digits, \
                                            '@' for email field")
                return HttpResponseRedirect(reverse('market:signup'))
            if password != confirm_password:
                messages.warning(request, "Passwords doesn't match.")
                return HttpResponseRedirect(reverse('market:signup'))
            if len(password) < 8:
                messages.warning(request, "Password must have 8 or more symbols.")
                return HttpResponseRedirect(reverse('market:signup'))
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                return HttpResponseRedirect(reverse("market:login"))
            except IntegrityError:
                messages.warning(request, "Username is already taken.")
                return HttpResponseRedirect(reverse("market:signup"))
    else:
        return render(request, "market/signup.html")


def login_view(request):
    if request.method == "POST":
        try:
            username = request.POST["username"]
            password = request.POST["password"]
        except KeyError:
            messages.warning(request, "You didn't fill all fields.")
            return HttpResponseRedirect(reverse("market:login"))
        else:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('market:index'))
            else:
                messages.warning(request, "Login data is invalid.")
                return HttpResponseRedirect(reverse("market:login"))

    return render(request, "market/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("market:index"))


@login_required
def watchlist(request):
    user = request.user
    if request.method == "POST":
        try:
            listing = get_object_or_404(AuctionListing, pk=request.POST['listing_id'])
        except KeyError:
            return HttpResponseRedirect(reverse("market:index"))
        if listing not in user.watchlist.all():
            user.watchlist.add(listing)
        else:
            user.watchlist.remove(listing)
        user.save()
        return HttpResponseRedirect(reverse("market:details", kwargs={"listing_id": listing.id}))
    else:
        return render(request, "market/index.html", {
            "active_listing_list": user.watchlist.all(),
            "watchlist": "Watchlist", })


@login_required
def removeListing(request):
    user = request.user
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=request.POST["listing_id"])
        if listing.user == request.user and not listing.active:
            listing.delete()
            return HttpResponseRedirect(reverse("market:index"))


@login_required
def mylistings(request):
    user = request.user
    return render(request, "market/index.html", {
        "active_listing_list": AuctionListing.objects.filter(user=user),
        "mylistings": "My Listings", })


# Don't need this for now cause few functions for listing was replaced on websocket
"""
@login_required
def endlisting(request):
    user = request.user
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=request.POST["listing_id"])
        if user == listing.user:
            listing.active = False
            listing.save()
            #Define winner
            bids = Bid.objects.filter(listing=listing)
            if bids is None:
                return HttpResponseRedirect(reverse("market:details", kwargs = {"listing_id":listing.id}))
            else:
                last_bid = bids.order_by("-value")[0]
                win_user = last_bid.user
                win_user.winlist.add(listing)
                new_chat = Chat.objects.create()
                new_chat.members.add(win_user, listing.user)
                new_message_text = f"Hi, you won my listing at link http://127.0.0.1:8000{reverse('market:details', kwargs = {'listing_id':listing.id})}"
                new_message = Message.objects.create(chat = new_chat, sender_id = listing.user.id, text = new_message_text)
                messages.warning(request, f"{last_bid.user.username}")
                return HttpResponseRedirect(reverse("market:details", kwargs = {"listing_id":listing.id}))
"""


def active_listing(request):
    return render(request, "market/index.html", {
        "active_listing_list": AuctionListing.objects.filter(active=True)})


class CategoriesView(generic.ListView):
    template_name = 'market/categories.html'
    context_object_name = 'categories'

    def get_queryset(self):
        """Return all listing that exist."""
        return Category.objects.all()


def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    return render(request, "market/index.html", {
        "active_listing_list": AuctionListing.objects.filter(category=category)})


@login_required
def comment(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        user = request.user
        commentValue = request.POST['comment'].strip()
        if commentValue and listing.active:
            new_comment = Comment.objects.create(date=timezone.now(), user=user, listing=listing, text=commentValue)
            new_comment.save()
        return HttpResponseRedirect(reverse("market:details", kwargs={"listing_id": listing.id}))
    return HttpResponseRedirect(reverse("market:index"))


@login_required
def sendcontact(request):
    if request.method == "POST":
        user = request.user
        listing = get_object_or_404(AuctionListing, pk=request.POST["listing_id"])
        try:
            email = request.POST['email']
        except KeyError:
            messages.warning(request, "Email Field is empty")
            return HttpResponseRedirect(reverse("market:details", kwargs={'listing_id': listing.id}))
        else:
            send_message = ChatMessage.objects.create(sender=user, text=email, user_id=listing.user.id)
            send_message.save()
            user.winlist.remove(listing)
            messages.success(request, "Your email was send to listing owner, wait for he contact with you.")
            return HttpResponseRedirect(reverse("market:details", kwargs={"listing_id": listing.id}))


@login_required
def winlistings(request):
    user = request.user
    if user.winlist.all():
        return render(request, "market/index.html", {
            "active_listing_list": user.winlist.all(),
            "winlist": "Winlist",
        })


@login_required
def inbox(request):
    user = request.user
    if request.method == "POST":
        try:
            choosen_user = User.objects.get(pk=int(request.POST['user_id']))
        except (KeyError, User.DoesNotExist, ValueError):
            messages.warning(request, "User not found :(")
            return HttpResponseRedirect(reverse("market:inbox"))
        else:
            check_chat = Chat.objects.filter(members=user.id).filter(members=choosen_user.id)
            if not check_chat:
                new_chat = Chat.objects.create()
                new_chat.members.add(user, choosen_user)
                new_chat.save()
                return HttpResponseRedirect(reverse("market:chat", kwargs={'chat_id': new_chat.id}))
            else:
                messages.warning(request, "Chat exist :(")
                return HttpResponseRedirect(reverse("market:inbox"))
    all_users = User.objects.all().exclude(pk=user.id)
    current_user_chats = Chat.objects.filter(members=user.id)
    for chat in current_user_chats:
        if chat.members.count() == 2:
            to_delete_member = chat.members.all().exclude(id=user.id)
            all_users = all_users.exclude(pk=to_delete_member.first().id)

    return render(request, "market/inbox.html", {
        "chats": current_user_chats,
        "site_users": all_users,
    })


@login_required
def chat(request, chat_id):
    user = request.user
    try:
        get_chat = Chat.objects.get(pk=chat_id)
    except Chat.DoesNotExist:
        return HttpResponseRedirect(reverse("market:inbox"))
    else:
        if user in get_chat.members.all():
            get_messages = Message.objects.filter(chat=get_chat).order_by('date')
            unread_messages_all = 0
            for chat_item in Chat.objects.filter(members=user):
                for message_item in chat_item.message_set.exclude(sender_id=user.id):
                    if chat_item == get_chat:
                        message_item.unread = False
                        message_item.save()
                    if message_item.unread:  # BooleanField 'unread' in Message
                        unread_messages_all += 1

            user.inbox = unread_messages_all
            user.save()
            return render(request, "market/chat.html", {
                "messages": get_messages,
                "chat": get_chat,
            })
        else:
            return HttpResponseRedirect(reverse("market:inbox"))


@login_required
def mybids(request):
    user = request.user
    listings = []
    if user.bid_set.all():
        for i in user.bid_set.all():
            if i.listing not in listings:
                listings.append(i.listing)
        return render(request, "market/index.html", {
            "active_listing_list": listings,
        })
    return HttpResponseRedirect(reverse("market:index"))


@login_required
def add_user_avatar(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)
    if request.user == user_instance:
        if request.method == "POST":
            form = UserAvatarForm(request.POST, request.FILES, instance=user_instance)
            if form.is_valid():
                form.save()
                user_obj = form.instance
                return render(request, 'market/usercabinet.html', {"form": form, "user_obj": user_obj})

        else:
            form = UserAvatarForm(instance=user_instance)
        return render(request, 'market/usercabinet.html', {'form': form, "user_obj": user_instance})
    else:
        return render(request, "market/index.html")


@csrf_exempt
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JsonResponse(result, status=200)
