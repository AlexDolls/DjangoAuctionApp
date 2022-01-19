from django.core.management.base import BaseCommand
from market.models import AuctionListing
from market.tasks import create_task
from django.utils import timezone

import urllib.request
import time
import datetime
from threading import Thread

def listing_date_checker():
    listings = AuctionListing.objects.all()
    for listing in listings:
        seconds_to_end = datetime.timedelta.total_seconds(listing.endDate - timezone.now())
        if seconds_to_end > 0:
            task = create_task.apply_async(kwargs = {"listing_id":listing.id}, countdown = seconds_to_end)

class Command(BaseCommand):
    help = "Sample task creator"

    def handle(self, *args, **options):
        background_thread = Thread(target = listing_date_checker)
        background_thread.start()
