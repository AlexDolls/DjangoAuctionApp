from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core import validators


class User(AbstractUser):
    watchlist = models.ManyToManyField('AuctionListing', blank=True, related_name='userWatchList')
    category = models.ManyToManyField('Category', blank=True, related_name="userCategories")
    winlist = models.ManyToManyField('AuctionListing', blank=True, related_name="userWinListings")
    inbox = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to="images", default="default-user.png")


class Chat(models.Model):
    members = models.ManyToManyField("User", blank=True, related_name="userChat")

    def serialize(self):
        return {
            "user": self.members.name
        }


class Message(models.Model):
    text = models.CharField(max_length=300)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_receiver", null=True)
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE)
    unread = models.BooleanField(default=True)
    date = models.DateTimeField(default=timezone.now())

    def serialize(self):
        return {
            "body": self.text,
            "sender": self.sender,
            "receiver": self.receiver,
            "chat": self.chat.id,
            "date": self.date
        }

    def preview(self):
        return f"{self.text[:10]}..."


class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.id} : {self.name}"


class AuctionListing(models.Model):
    name = models.CharField(max_length=32)
    image = models.URLField(blank=True)
    loaded_image = models.ImageField(upload_to="images", validators=[
        validators.FileExtensionValidator(['jpg', 'png'], message="File must be image")], blank=True)
    description = models.CharField(max_length=150)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    startBid = models.DecimalField(decimal_places=2, max_digits=7)
    creationDate = models.DateTimeField()
    endDate = models.DateTimeField()
    active = models.BooleanField()

    def __str__(self):
        return f"ID: {self.id}\nUser: {self.user}\nName: {self.name}\nCategory: {self.category}\nDescription: {self.description}\nStart Bid: {self.startBid}\nCreated: {self.creationDate}\nEnd at: {self.endDate}\nActive: {self.active}"


class Bid(models.Model):
    value = models.DecimalField(decimal_places=2, max_digits=7)
    listing = models.ForeignKey('AuctionListing', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    date = models.DateTimeField()


class Comment(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    listing = models.ForeignKey('AuctionListing', on_delete=models.CASCADE)
