import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import User, Category, AuctionListing, Bid, Comment

def create_user(username, password):
    """
    Creating user instance for test with models that need to be attach to user and views that works only with authorized users
    """
    user = User.objects.create(username = username)
    user.set_password(password)
    user.save()
    return user

def create_listing(name, image, description, category, user, startBid, days, active):
    """
    Create Listing with given "name", "image", "description", "category", "user", "startBid", "days", "active".
    The start date of listing is timezone.now() and end date is start date + offset by "days" value.
    """
    start_date = timezone.now()
    end_date = start_date + datetime.timedelta(days)
    return AuctionListing.objects.create(name = name, image = image, description = description, category = category, user = user, startBid = startBid, creationDate = start_date, endDate = end_date, active = active)

def create_category(name):
    """
    Create category with given "name".
    """
    category = Category.objects.create(name = name)
    category.save()
    return category

def isfloat(a):
    try:
        a = float(a)
    except ValueError:
        pass
    else:
        return True


class ListingCreationViewTests(TestCase):
    def test_empty_post_data(self):
        """
        If no POST data - Redirect to listing's creation page
        """
        user_password = "password"
        user_name = "test_user"
        user = create_user(username = user_name, password = user_password)
        post_data = {}

        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:createListing"))

    def test_full_post_data(self):
        """
        If POST data full and correct - Redirect to created listing page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"
        
        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "imageurl":"None",
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertEqual(response.url, reverse("market:details", kwargs = {"listing_id":AuctionListing.objects.get(name = "Test_Listing").id,}))

    def test_empty_listingname_post_data(self):
        """
        if listingname POST data does not exist - Redirect to listing's creation page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"category":category.id,
                "startBid":100,
                "imageurl":"None",
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:createListing"))
    
    def test_empty_category_post_data(self):
        """
        if category POST data does not exist - Redirect to listing's creation page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "startBid":100,
                "imageurl":"None",
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:createListing"))

    def test_empty_startBid_post_data(self):
        """
        if startBid POST data does not exist - Redirect to listing's creation page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "imageurl":"None",
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:createListing"))

    def test_empty_imageurl_post_data(self):
        """
        if imageurl POST data does not exist - Redirect to listing's creation page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:createListing"))

    def test_empty_listingdesc_post_data(self):
        """
        if listingdesc POST data does not exist - Redirect to listing's creation page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "imageurl":"None",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:createListing"))

    def test_incorrect_listingname_value_post_data(self):
        """
        If listingname POST data is numeric - Redirect to created listing page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":1,
                "category":category.id,
                "startBid":100,
                "imageurl":"None",
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertEqual(response.url, reverse("market:details", kwargs = {"listing_id":AuctionListing.objects.get(name ="1").id,}))

    def test_incorrect_category_value_post_data(self):
        """
        If category POST data is incorrect - Redirect to listing's creation page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":"category.id",
                "startBid":100,
                "imageurl":"None",
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:createListing"))

    def test_incorrect_startBid_value_post_data(self):
        """
        If startBid POST data is incorrect - Redirect to listing's creation page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":"startBid",
                "imageurl":"None",
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:createListing"))

    def test_incorrect_imageurl_value_post_data(self):
        """
        If imageurl POST data is numeric - Redirect to created listing page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "imageurl":1,
                "listingdesc":"Test_Description",}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertEqual(response.url, reverse("market:details", kwargs = {"listing_id":AuctionListing.objects.get(name = "Test_Listing").id,}))

    def test_incorrect_listingdesc_value_post_data(self):
        """
        If listingdesc POST data is numeric - Redirect to created listing page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "imageurl":"None",
                "listingdesc":1,}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertEqual(response.url, reverse("market:details", kwargs = {"listing_id":AuctionListing.objects.get(name = "Test_Listing").id,}))
    
class ListingIndexView(TestCase):
    def test_all_listings_are_displayed_on_page(self):
        """
        Authorized user.
        Checking that listings with a full set of combinations (In watchlist + Not active, Not in watchlist + Not active, In watchlist + Active, Not in watchlist + not active) are displayed by IndexView
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        #this listing will be added in user's watchlist and Not active
        listing_watchlist_not_active = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
        #this listing won't be added in user's watchlist and  Not active
        listing_not_watchlist_not_active = create_listing(name = "listing_2", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
        #this listing will be added in user's watchlist and Active
        listing_watchlist_active = create_listing(name = "listing_3", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
        #this listing won't be added in user's watchlist and Active
        listing_not_watchlist_active = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)

        user.watchlist.add(listing_watchlist_not_active, listing_watchlist_active)
        self.client.login(username = user_name, password = user_password)
        response = self.client.get(reverse("market:index"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_watchlist_not_active, listing_not_watchlist_not_active, listing_watchlist_active, listing_not_watchlist_active])
        self.assertContains(response, "listing_1")
        self.assertContains(response, "listing_2")
        self.assertContains(response, "listing_3")
        self.assertContains(response, "listing_4")
        self.assertContains(response, "Auction Listings")

class ListingActiveView(TestCase):
    def test_only_active_listings_on_page(self):
        """
        Authorized user
        Only active and (in/not_in watchlist) listings are displayed on Active page.
        """

        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        #this listing will be added in user's watchlist and Not active
        listing_not_active_watchlist = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
        #this listing won't be added in user's watchlist and  Not active
        listing_not_active_not_watchlist = create_listing(name = "listing_2", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
        #this listing will be added in user's watchlist and Active
        listing_active_watchlist = create_listing(name = "listing_3", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)
        #this listing won't be added in user's watchlist and Active
        listing_active_not_watchlist = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)

        user.watchlist.add(listing_active_watchlist, listing_not_active_watchlist)
        response = self.client.get(reverse("market:active"))
        self.client.login(username = user_name, password = user_password)
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_active_watchlist, listing_active_not_watchlist])

