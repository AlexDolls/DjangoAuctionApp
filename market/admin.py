from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(Category)
admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Chat)
admin.site.register(Message)
