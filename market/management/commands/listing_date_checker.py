from django.core.management.base import BaseCommand
from market.models import AuctionListing
from django.utils import timezone

import time
import datetime
from threading import Thread

def listing_date_checker():
    while True:
        time.sleep(60)
        all_listings = AuctionListing.objects.all()
        if all_listings:
            for listing in all_listings:
                if listing.endDate < timezone.now():
                    listing.active = False
                    listing.save()
        

class Command(BaseCommand):
    help = "The listing date checker"

    def handle(self, *args, **options):
        background_thread = Thread(target = listing_date_checker)
        background_thread.start()
