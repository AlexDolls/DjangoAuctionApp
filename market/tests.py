import datetime
import pytest

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import User, Category, AuctionListing, Bid, Comment, Chat, Message

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
    Create category wit
    h given "name".
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
        category_1_name = "category_1"
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"
        hours = "12"
        
        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "imageurl":"None",
                "listingdesc":"Test_Description",
                "expiretime":hours,}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, reverse("market:details", kwargs = {"listing_id":AuctionListing.objects.get(name = "Test_Listing").id,}))

    def test_get_request_for_not_logged_in_user(self):
        """
        If not logged in user try to request the creation page - return login request.
        """
        response = self.client.get(reverse("market:createListing"))
        self.assertURLEqual(response.url, f"/accounts/login/?next={reverse('market:createListing')}")

    def test_get_request_for_logged_in_user(self):
        """
        If logged in user try to request the creation page - return 200 status code.
        """
        user_password = "password"
        user_name = "test_user"

        user = create_user(username = user_name, password = user_password)
        self.client.login(username = user_name, password = user_password)
        response = self.client.get(reverse("market:createListing"))
        self.assertEqual(response.status_code, 200)

    def test_post_request_for_not_logged_in_user(self):
        """
        If not logged in user try to send post request - return login request
        """
        category_1_name = "category_1"

        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "imageurl":"None",
                "listingdesc":"Test_Description",}
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertURLEqual(response.url, f"/accounts/login/?next={reverse('market:createListing')}")

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
        hours = "12"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":1,
                "category":category.id,
                "startBid":100,
                "imageurl":"None",
                "listingdesc":"Test_Description",
                "expiretime":hours,}
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
        hours = "12"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "imageurl":1,
                "listingdesc":"Test_Description",
                "expiretime":hours}
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
        hours = "12"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)
        post_data = {"listingname":"Test_Listing",
                "category":category.id,
                "startBid":100,
                "imageurl":"None",
                "listingdesc":1,
                "expiretime":hours}
        self.client.login(username = user_name, password = user_password)
        response = self.client.post(reverse("market:createListing"), post_data)
        self.assertEqual(response.url, reverse("market:details", kwargs = {"listing_id":AuctionListing.objects.get(name = "Test_Listing").id,}))
    
class ListingIndexViewTests(TestCase):
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

    def test_all_listings_are_displayed_on_page_not_logged_in(self):
        """
        Not Authorized user.
        Checking that listings with a full set of combinations (Not active, Active) are displayed by IndexView
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)

        listing_not_active = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
        listing_active = create_listing(name = "listing_2", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)

        response = self.client.get(reverse("market:index"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active, listing_active])
        self.assertContains(response, "listing_1")
        self.assertContains(response, "listing_2")
        self.assertContains(response, "Auction Listings")


class ListingActiveViewTests(TestCase):
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

    def test_only_active_listings_displayed_not_logged_in(self):
        """
        Not Authorized user.
        Checking that only active listings are displayed on Active page.
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"

        user = create_user(username = user_name, password = user_password)
        category = create_category(name = category_1_name)

        listing_not_active = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = False)
        listing_active = create_listing(name = "listing_2", image = "None", description = "test_desc", category = category, user=user, startBid=100, days=30, active = True)

        response = self.client.get(reverse("market:active"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_active])


class CategoryViewTests(TestCase):
    def test_2_categories_displayed_logged_in_user(self):
        """
        Authorized user
        Created both categories are displayed on By Categories page
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"
        category_2_name = "category_2"

        user = create_user(username = user_name, password = user_password)
        category_1 = create_category(name = category_1_name)
        category_2 = create_category(name = category_2_name)
        
        self.client.login(username=user_name, password = user_password)
        response = self.client.get(reverse("market:categories"))
        self.assertQuerysetEqual(list(response.context['categories']), [category_1, category_2])

    def test_2_categories_displayed_not_logged_in_user(self):
        """
        Not Authorized user
        Created both categories are displayed on By Categories page
        """
        category_1_name = "category_1"
        category_2_name = "category_2"

        category_1 = create_category(name = category_1_name)
        category_2 = create_category(name = category_2_name)
        response = self.client.get(reverse("market:categories"))
        self.assertQuerysetEqual(list(response.context['categories']), [category_1, category_2])

class CategoryListingsViewTests(TestCase):
    def test_category_not_exist_logged_in_user(self):
        """
        Authorized User
        If category not exist - return status code 404
        """
        user_password = "password"
        user_name = "test_user"

        user = create_user(username = user_name, password = user_password)

        self.client.login(username=user_name, password = user_password)
        response = self.client.get(reverse("market:category_listings", kwargs = {"category_id":1}))
        self.assertEqual(response.status_code, 404)

    def test_category_not_exist_not_logged_in_user(self):
        """
        Not Authorized User
        If category not exist - return status code 404
        """
        response = self.client.get(reverse("market:category_listings", kwargs = {"category_id":1}))
        self.assertEqual(response.status_code, 404)

    def test_two_listings_different_categories_logged_in_user(self):
        """
        Authorized user
        From all listings combinations with two different categories will be shown only those with choseen category (category_1)
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"
        category_2_name = "category_2"

        user = create_user(username = user_name, password = user_password)
        category_1 = create_category(name = category_1_name)
        category_2 = create_category(name = category_2_name)
        
        #this listing will be added in user's watchlist and Not active - category_1
        listing_not_active_watchlist_category_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user, startBid=100, days=30, active = False)
        #this listing won't be added in user's watchlist and  Not active - category_1
        listing_not_active_not_watchlist_category_1 = create_listing(name = "listing_2", image = "None", description = "test_desc", category = category_1, user=user, startBid=100, days=30, active = False)
        #this listing will be added in user's watchlist and Active - category_1
        listing_active_watchlist_category_1 = create_listing(name = "listing_3", image = "None", description = "test_desc", category = category_1, user=user, startBid=100, days=30, active = True)
        #this listing won't be added in user's watchlist and Active - category_1
        listing_active_not_watchlist_category_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user, startBid=100, days=30, active = True)

        #this listing will be added in user's watchlist and Not active - category_2
        listing_not_active_watchlist_category_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_2, user=user, startBid=100, days=30, active = False)
        #this listing won't be added in user's watchlist and  Not active - category_2
        listing_not_active_not_watchlist_category_2 = create_listing(name = "listing_2", image = "None", description = "test_desc", category = category_2, user=user, startBid=100, days=30, active = False)
        #this listing will be added in user's watchlist and Active - category_2
        listing_active_watchlist_category_2 = create_listing(name = "listing_3", image = "None", description = "test_desc", category = category_2, user=user, startBid=100, days=30, active = True)
        #this listing won't be added in user's watchlist and Active - category_2
        listing_active_not_watchlist_category_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_2, user=user, startBid=100, days=30, active = True)

        user.watchlist.add(listing_active_watchlist_category_1, listing_not_active_watchlist_category_1, listing_active_watchlist_category_2, listing_not_active_watchlist_category_2)

        self.client.login(username=user_name, password = user_password)
        response = self.client.get(reverse("market:category_listings", kwargs = {"category_id":category_1.id}))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_watchlist_category_1, listing_not_active_not_watchlist_category_1, listing_active_watchlist_category_1, listing_active_not_watchlist_category_1])

    def test_two_listings_different_categories_not_logged_in_user(self):
        """
        Not Authorized user
        From all listings combinations with two different categories will be shown only those with choseen category (category_1)
        """
        user_password = "password"
        user_name = "test_user"
        category_1_name = "category_1"
        category_2_name = "category_2"

        user = create_user(username = user_name, password = user_password)
        category_1 = create_category(name = category_1_name)
        category_2 = create_category(name = category_2_name)

        #this listing will be added in user's watchlist and Not active - category_1
        listing_not_active_watchlist_category_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user, startBid=100, days=30, active = False)
        #this listing won't be added in user's watchlist and  Not active - category_1
        listing_not_active_not_watchlist_category_1 = create_listing(name = "listing_2", image = "None", description = "test_desc", category = category_1, user=user, startBid=100, days=30, active = False)
        #this listing will be added in user's watchlist and Active - category_1
        listing_active_watchlist_category_1 = create_listing(name = "listing_3", image = "None", description = "test_desc", category = category_1, user=user, startBid=100, days=30, active = True)
        #this listing won't be added in user's watchlist and Active - category_1
        listing_active_not_watchlist_category_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user, startBid=100, days=30, active = True)

        #this listing will be added in user's watchlist and Not active - category_2
        listing_not_active_watchlist_category_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_2, user=user, startBid=100, days=30, active = False)
        #this listing won't be added in user's watchlist and  Not active - category_2
        listing_not_active_not_watchlist_category_2 = create_listing(name = "listing_2", image = "None", description = "test_desc", category = category_2, user=user, startBid=100, days=30, active = False)
        #this listing will be added in user's watchlist and Active - category_2
        listing_active_watchlist_category_2 = create_listing(name = "listing_3", image = "None", description = "test_desc", category = category_2, user=user, startBid=100, days=30, active = True)
        #this listing won't be added in user's watchlist and Active - category_2
        listing_active_not_watchlist_category_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_2, user=user, startBid=100, days=30, active = True)

        response = self.client.get(reverse("market:category_listings", kwargs = {"category_id":category_1.id}))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_watchlist_category_1, listing_not_active_not_watchlist_category_1, listing_active_watchlist_category_1, listing_active_not_watchlist_category_1])
 
class MyListingsViewTests(TestCase):
    def test_no_my_listings(self):
        """
        If user(user_1) created no listings and have empty watchlist - show appropriate message on page My Listings
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:mylistings"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [])
        self.assertContains(response, "No items Available")

    def test_no_my_listings_watchlist(self):
        """
        If user(user_1) created no listings and have listings of other user in his watchlist - No listings displayed on My Listings page.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)
        
        user_1.watchlist.add(listing_not_active_user_2, listing_active_user_2)

        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:mylistings"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [])
        self.assertContains(response, "No items Available")

    def test_exist_only_my_listings(self):
        """
        If user(user_1) created listings - Only his listings displayed on My Listings page. No listings created by other users
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:mylistings"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_user_1, listing_active_user_1])

    def test_exist_only_my_listings_watchlist(self):
        """
        If user(user_1) created listings and added it to watchlist - Only all of his listings displayed on My Listings page. No listings created by other users
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        
        user_1.watchlist.add(listing_not_active_user_1, listing_active_user_1)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:mylistings"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_user_1, listing_active_user_1])

    def test_exist_not_only_my_listings(self):
        """
        If user(user_1) created listings - Only his listings displayed on My Listings page. Two listings created by other user
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:mylistings"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_user_1, listing_active_user_1])

    def test_exist_not_only_my_listings_watchlist(self):
        """
        If user(user_1) created listings - Only his listings displayed on My Listings page. Two listings created by other user. All listings was added to user_1 watchlist
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        
        user_1.watchlist.add(listing_not_active_user_2, listing_active_user_2, listing_not_active_user_1, listing_active_user_1)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:mylistings"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_user_1, listing_active_user_1])

class WatchlistViewTests(TestCase):
    def test_unauthorized_user_GET_request(self):
        """
        If user is not Authorized - return login required page on GET request
        """
        response = self.client.get(reverse("market:watchlist"))
        self.assertURLEqual(response.url, f"/accounts/login/?next={reverse('market:watchlist')}")

    def test_unauthorized_user_empty_query_POST_request_add_to_watchlist(self):
        """
        If user is not Authorized and trying to send request Add to Watchlist - return login required page on POST request with empty query
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)
        listing = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        response = self.client.post(reverse("market:watchlist"))
        self.assertURLEqual(response.url, f"/accounts/login/?next={reverse('market:watchlist')}")

    def test_unauthorized_user_right_query_data_POST_request_add_to_watchlist(self):
        """
        If user is not Authorized and trying to send request Add to Watchlist - return login required page on POST request with right data in query
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"
        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)
        listing = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        response = self.client.post(reverse("market:watchlist"), {"listing_id":listing.id})
        self.assertURLEqual(response.url, f"/accounts/login/?next={reverse('market:watchlist')}")
        
    def test_unauthorized_user_wrong_query_data_POST_request_add_to_watchlist(self):
        """
        If user is not Authorized and trying to send request Add to Watchlist - return login required page on POST request with wrong data in query
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)
        listing = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        response = self.client.post(reverse("market:watchlist"), {"listing_id":2})
        self.assertURLEqual(response.url, f"/accounts/login/?next={reverse('market:watchlist')}")

    def test_authorized_user_empty_query_POST_request_add_to_watchlist(self):
        """
        If user is Authorized and trying to send request Add to Watchlist - redirect to index page and add nothing to user's watchlist by POST request with empty query
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)
        listing = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:watchlist"))
        self.assertURLEqual(response.url, reverse("market:index"))
        self.assertQuerysetEqual(user_1.watchlist.all(),[])

    def test_authorized_user_right_query_data_POST_request_add_to_watchlist(self):
        """
        If user is Authorized and trying to send request Add to Watchlist - add choosen listing to user's watchlist by POST request with right data in query
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)
        listing = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:watchlist"), {"listing_id":listing.id})
        self.assertQuerysetEqual(user_1.watchlist.all(), [listing])
        
    def test_authorized_user_wrong_query_data_POST_request_add_to_watchlist(self):
        """
        If user is Authorized and trying to send request Add to Watchlist- return 404 page and add nothing to user's watchlist by POST request with wrong data in query
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:watchlist"), {"listing_id":2})
        self.assertEqual(response.status_code, 404)
        self.assertQuerysetEqual(user_1.watchlist.all(),[])

    def test_two_users_one_listing_watchlist_add(self):
        """
        if exist two users and one listing, when first user adding listings to his watchlist, second user's wathclist still empty
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)
        listing = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:watchlist"), {"listing_id":listing.id})
        self.assertQuerysetEqual(user_1.watchlist.all(), [listing])
        self.assertQuerysetEqual(user_2.watchlist.all(), [])

    def test_remove_from_watchlist(self):
        """
        If user is Authorized and trying to send request to remove listing from Watchlist - remove choosen listing from user's watchlist
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)
        listing = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        user_1.watchlist.add(listing)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:watchlist"), {"listing_id":listing.id})
        self.assertQuerysetEqual(user_1.watchlist.all(), [])

    def test_two_users_remove_from_watchlist(self):
        """
        Exist two users and one listing, both have this listing in their watchlist, first user removing listing from his watchlist, then he has empty watchlist, second user still have this listing in his watchlist.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)
        listing = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        user_1.watchlist.add(listing)
        user_2.watchlist.add(listing)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:watchlist"), {"listing_id":listing.id})
        self.assertQuerysetEqual(user_1.watchlist.all(), [])
        self.assertQuerysetEqual(user_2.watchlist.all(), [listing])


    def test_own_and_other_owner_listings_in_watchlist(self):
        """
        If user(user_1) will add his own listings and listings of other user in watchlist - all added listings will displayed
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        user_1.watchlist.add(listing_not_active_user_2, listing_active_user_2, listing_not_active_user_1, listing_active_user_1)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:watchlist"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_active_user_1, listing_not_active_user_1, listing_active_user_2, listing_not_active_user_2], ordered = False)

    def test_no_listings_in_watchlist(self):
        """
        If user(user_1) will not add any of his own listings and listings of other user in watchlist - nothing will displayed on Watchlist page - appropriate message will displayed.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:watchlist"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [])
        self.assertContains(response, "No items Available")

    def test_only_other_user_listings_in_watchlist(self):
        """
        if user(user_1) added only listings of other user to watchlist - only added listings will displayed
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        user_1.watchlist.add(listing_not_active_user_2, listing_active_user_2)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:watchlist"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_user_2, listing_active_user_2])

    def test_only_own_listings_in_watchlist(self):
        """
        if user(user_1) added only own listings to watchlist - only added listings will displayed
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        user_1.watchlist.add(listing_not_active_user_1, listing_active_user_1)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:watchlist"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_user_1, listing_active_user_1])

    def test_one_active_not_own_listing(self):
        """
        Exist 4 listings. 2 own (Active and not Active) and same set from other owner. One Active listing of other owner added to own watchlist - only this listing will be displayed on Watchlist page.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        user_1.watchlist.add(listing_active_user_2)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:watchlist"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_active_user_2])

    def test_one_not_active_not_own_listing(self):
        """ 
        Exist 4 listings. 2 own (Active and not Active) and same set from other owner. One Not Active listing of other owner added to own watchlist - only this listing will be displayed on Watchlist page.
        """ 
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        user_1.watchlist.add(listing_not_active_user_2)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:watchlist"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_user_2])

    def test_one_active_own_listing(self):
        """
        Exist 4 listings. 2 own (Active and not Active) and same set from other owner. One Active Own listing added to own watchlist - only this listing will be displayed on Watchlist page.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        user_1.watchlist.add(listing_active_user_1)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:watchlist"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_active_user_1])

    def test_one_not_active_own_listing(self):
        """
        Exist 4 listings. 2 own (Active and not Active) and same set from other owner. One Not Active Own listing added to own watchlist - only this listing will be displayed on Watchlist page.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)

        #Not active - user_2
        listing_not_active_user_2 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = False)
        #Active - user_2
        listing_active_user_2 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_2, startBid=100, days=30, active = True)

        #Not active - user_1
        listing_not_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        #Active - user_1
        listing_active_user_1 = create_listing(name = "listing_4", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)

        user_1.watchlist.add(listing_not_active_user_1)
        self.client.login(username=user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:watchlist"))
        self.assertQuerysetEqual(list(response.context['active_listing_list']), [listing_not_active_user_1])

class InboxViewTests(TestCase):
    def test_uathorized_user_inbox(self):
        """
        if Not Authorized user trying to get inbox page - return login required page
        """
        response = self.client.get(reverse("market:inbox"))
        self.assertURLEqual(response.url, f"/accounts/login/?next={reverse('market:inbox')}")

    def test_no_chats_with_user_exist_no_other_users_exist(self):
        """
        If no chats with current user as member exist.No other users exist. Show appropriate messages on inbox page
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have no chat's yet")
        self.assertQuerysetEqual(response.context['chats'],[])
        self.assertContains(response, "There's no users to start chat with for now :(")
        self.assertQuerysetEqual(response.context['site_users'], [])

    def test_no_chats_with_user_exist_other_user_exist(self):
        """
        If no chats with current user as member exist.One other user exists. Show appropriate messages on inbox page
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have no chat's yet")
        self.assertQuerysetEqual(response.context['chats'], [])
        self.assertContains(response, "Start!")
        self.assertQuerysetEqual(response.context['site_users'], [user_2])

    def test_chat_with_user_exist_other_user_exist(self):
        """
        If chat with current user as member exists.One other user exists. Show appropriate messages on inbox page
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        chat_new = Chat.objects.create()
        chat_new.members.add(user_1, user_2)
        chat_new.save()
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['chats'], [chat_new])
        self.assertQuerysetEqual(response.context['site_users'], [])
        self.assertContains(response, "There's no users to start chat with for now :(")


    def test_no_chats_with_user_two_users_exist(self):
        """
        If no chats with current user as member exist.Two other users exist. Show appropriate messages on inbox page
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        user_password_3 = "password_2"
        user_name_3 = "test_user_3"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        user_3 = create_user(username = user_name_3, password = user_password_3)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have no chat's yet")
        self.assertQuerysetEqual(response.context['chats'], [])
        self.assertContains(response, "Start!")
        self.assertQuerysetEqual(list(response.context['site_users']), [user_2, user_3])

    def test_chat_with_user_exist_two_users_exist(self):
        """
        If one chat with current user as member exists.Two other users exist. Show appropriate messages on inbox page
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        user_password_3 = "password_2"
        user_name_3 = "test_user_3"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        user_3 = create_user(username = user_name_3, password = user_password_3)
        chat_new = Chat.objects.create()
        chat_new.save()
        chat_new.members.add(user_1,user_2)
        chat_new.save()
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['chats'], [chat_new])
        self.assertContains(response, "Start!")
        self.assertQuerysetEqual(list(response.context['site_users']), [user_3])

    def test_start_chat_with_user_unathorized(self):
        """
        If user Not Authorized and sends request to start chat with exists user - return login required page.       
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_1 = create_user(username = user_name_1, password = user_password_1)
        
        response = self.client.post(reverse("market:inbox"), {"user_id":user_1.id})
        self.assertURLEqual(response.url, f"/accounts/login/?next={reverse('market:inbox')}")

    def test_start_new_chat_with_user(self):
        """
        if user starts new chat with user - chat will be created and page will be showed
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:inbox"), {"user_id":user_2.id})
        self.assertQuerysetEqual(list(Chat.objects.get(members=user_1).members.all()), [user_1, user_2], ordered = False)

    def test_start_exist_chat_with_user(self):
        """
        if user starts new chat with user, but chat between that users already exists - chat will be not created
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        chat_new = Chat.objects.create()
        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        chat_new.members.add(user_1, user_2)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:inbox"), {"user_id":user_2.id})
        self.assertQuerysetEqual(Chat.objects.all(), [chat_new])
        self.assertURLEqual(response.url, reverse("market:inbox"))

    def test_start_new_chat_with_wrong_user_id(self):
        """
        if user starts new chat with wrong user's id entered, chat will not be created - 404 page returns
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.post(reverse("market:inbox"), {"user_id":user_2.id + 10})
        self.assertQuerysetEqual(Chat.objects.all(), [])
        self.assertURLEqual(response.url, reverse("market:inbox"))

class ChatViewTests(TestCase):
    def test_get_chat_user_unathorized(self):
        """
        if user is Not Authorized and try to get chat view - return login required page
        """
        response = self.client.get(reverse("market:chat", kwargs = {"chat_id":1}))
        self.assertURLEqual(response.url, f"/accounts/login/?next="+reverse("market:chat",kwargs={"chat_id":1}))

    def test_get_exists_chat_two_users(self):
        """
        if chat between two users as members exists.No messages exist. Display chat page with no messages.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        new_chat = Chat.objects.create()
        new_chat.members.add(user_1, user_2)
        new_chat.save()
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:chat", kwargs = {"chat_id":new_chat.id}))
        self.assertEqual(response.status_code, 200)
        #self.assertContains(response, user_2.username)
        self.assertEqual(response.context['chat'], new_chat)
        self.assertQuerysetEqual(response.context['messages'], [])

    def test_get_one_member_chat_two_users(self):
        """
        if chat exists only with one user of two existing. No messages exist. Display chat page with no messages. Only for one user.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        new_chat = Chat.objects.create()
        new_chat.members.add(user_1)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:chat", kwargs = {"chat_id":new_chat.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chat'], new_chat)
        self.assertQuerysetEqual(response.context['messages'], [])

    def test_get_user_is_not_member_chat_two_users(self):
        """
        if chat exist, but user is not that chat's member. No messages exist. Redirect to inbox page.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        new_chat = Chat.objects.create()
        new_chat.members.add(user_2)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:chat", kwargs = {"chat_id":new_chat.id}))
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, reverse("market:inbox"))

    def test_get_no_members_chat(self):
        """
        if chat exist, but user is not that chat's member. No messages exist. Redirect to inbox page.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        new_chat = Chat.objects.create()
        new_chat.members.add()
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:chat", kwargs = {"chat_id":new_chat.id}))
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, reverse("market:inbox"))

    def test_get_exists_chat_two_users_two_messages(self):
        """
        if chat between two users as members exists. Two messages exist. Display chat page with two messages.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        new_chat = Chat.objects.create()
        new_chat.members.add(user_1, user_2)
        message_user_1 = Message.objects.create(text="message_1", sender_id = user_1.id, chat = new_chat)
        message_user_2 = Message.objects.create(text="message_2", sender_id = user_2.id, chat = new_chat)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:chat", kwargs = {"chat_id":new_chat.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user_2.username)
        self.assertEqual(response.context['chat'], new_chat)
        self.assertQuerysetEqual(response.context['messages'], [message_user_1, message_user_2])

    def test_get_one_member_chat_two_users_one_message(self):
        """
        if chat exists only with one user of two existing as member. One message exists. Display chat page with one messages. Only for one user.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        new_chat = Chat.objects.create()
        new_chat.members.add(user_1)
        message_user_1 = Message.objects.create(text="message_1", sender_id = user_1.id, chat = new_chat)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:chat", kwargs = {"chat_id":new_chat.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['chat'], new_chat)
        self.assertQuerysetEqual(response.context['messages'], [message_user_1])

    def test_get_not_exist_chat(self):
        """
        if chat is not exist. Redirect to inbox page.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:chat", kwargs = {"chat_id":1}))
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, reverse("market:inbox"))

class DetailsViewTests(TestCase):
    def test_active_listing_detail_page_unauthorized(self):
        """
        if user is Not Authorized - display page of active listing with full info, but without any manage or action interface elements: "Make bid", "End Listing", "Delete Listing", "Add to Watchlist" buttons, excluding "Show history" button. Comment-input form.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)
        listing_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        response = self.client.get(reverse("market:details", kwargs = {"listing_id":listing_active_user_1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["true_user"], False)
        self.assertEqual(response.context['auctionlisting'], listing_active_user_1)
        self.assertQuerysetEqual(response.context['bids'], [])
        self.assertQuerysetEqual(response.context['comments'], [])
        self.assertEqual(response.context['bid'], None)
        self.assertContains(response, listing_active_user_1.name)
        self.assertContains(response, listing_active_user_1.description)
        self.assertContains(response, listing_active_user_1.user.username)
        self.assertContains(response, listing_active_user_1.startBid)
        self.assertContains(response, 'id = "show-history"')
        self.assertNotContains(response, 'id = "new-bid-submit"')
        self.assertNotContains(response, 'id = "newbid"')
        self.assertNotContains(response, 'id = "comment-submit"')
        self.assertNotContains(response, 'id = "add-listing-to_watchlist"')
        self.assertNotContains(response, 'id = "edit-listing"')
        self.assertNotContains(response, 'id = "end-listing-submit"')
        self.assertNotContains(response, 'id = "delete-listing"')
        self.assertNotContains(response, 'id = "winner-of-listing"')
        self.assertNotContains(response, 'id = "listing-is-ended"')
        self.assertNotContains(response, 'id = "last-price"')

    def test_active_listing_detail_page(self):
        """
        if user is Authorized but not listing's creator - display page of active listing with full info, but without creator's manage or action interface elements: "End Listing", "Delete Listing" buttons, excluding "Show history" button
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)
        listing_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        self.client.login(username = user_name_2, password = user_password_2)
        response = self.client.get(reverse("market:details", kwargs = {"listing_id":listing_active_user_1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["true_user"], False)
        self.assertEqual(response.context['auctionlisting'], listing_active_user_1)
        self.assertQuerysetEqual(response.context['bids'], [])
        self.assertQuerysetEqual(response.context['comments'], [])
        self.assertEqual(response.context['bid'], None)
        self.assertContains(response, listing_active_user_1.name)
        self.assertContains(response, listing_active_user_1.description)
        self.assertContains(response, listing_active_user_1.user.username)
        self.assertContains(response, listing_active_user_1.startBid)
        self.assertContains(response, 'id = "new-bid-submit"')
        self.assertContains(response, 'id = "newbid"')
        self.assertContains(response, 'id = "comment-submit"')
        self.assertContains(response, 'id = "add-listing-to-watchlist"')
        self.assertNotContains(response, 'id = "edit-listing"')
        self.assertNotContains(response, 'id = "end-listing-submit"')
        self.assertNotContains(response, 'id = "delete-listing"')
        self.assertNotContains(response, 'id = "winner-of-listing"')
        self.assertNotContains(response, 'id = "listing-is-ended"')
        self.assertNotContains(response, 'id = "last-price"')

    def test_active_listing_detail_page_creator(self):
        """
        if user is Authorized and listing's creator - display page of active listing with full info and full lising's manage interface elements, but without "Make bid" button
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)
        listing_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = True)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:details", kwargs = {"listing_id":listing_active_user_1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["true_user"], True)
        self.assertEqual(response.context['auctionlisting'], listing_active_user_1)
        self.assertQuerysetEqual(response.context['bids'], [])
        self.assertQuerysetEqual(response.context['comments'], [])
        self.assertEqual(response.context['bid'], None)
        self.assertContains(response, listing_active_user_1.name)
        self.assertContains(response, listing_active_user_1.description)
        self.assertContains(response, listing_active_user_1.user.username)
        self.assertContains(response, listing_active_user_1.startBid)
        self.assertContains(response, 'id = "last-bid"')
        self.assertContains(response, 'id = "comment-submit"')
        self.assertContains(response, 'id = "add-listing-to-watchlist"')
        self.assertContains(response, 'id = "edit-listing"')
        self.assertNotContains(response, 'id = "new-bid-submit"')
        self.assertNotContains(response, 'id = "newbid"')
        self.assertNotContains(response, 'id = "winner-of-listing"')
        self.assertNotContains(response, 'id = "listing-is-ended"')
        self.assertNotContains(response, 'id = "last-price"')

    def test_not_active_listing_detail_page_unauthorized(self):
        """
        if user is Not Authorized - display page of not active listing with full info and message that listing is ended, but without any manage or action interface elements: "Make bid", "End Listing", "Delete Listing", "Add to Watchlist" buttons, excluding "Show history" button. Comment-input form.
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        category_1 = create_category(name = category_1_name)
        listing_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        response = self.client.get(reverse("market:details", kwargs = {"listing_id":listing_active_user_1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["true_user"], False)
        self.assertEqual(response.context['auctionlisting'], listing_active_user_1)
        self.assertQuerysetEqual(response.context['bids'], [])
        self.assertQuerysetEqual(response.context['comments'], [])
        self.assertEqual(response.context['bid'], None)
        self.assertContains(response, listing_active_user_1.name)
        self.assertContains(response, listing_active_user_1.description)
        self.assertContains(response, listing_active_user_1.user.username)
        self.assertContains(response, listing_active_user_1.startBid)
        self.assertContains(response, 'id = "show-history"')
        self.assertContains(response, 'id = "last-price"')
        self.assertContains(response, 'id = "listing-is-ended"')
        self.assertNotContains(response, 'id = "new-bid-submit"')
        self.assertNotContains(response, 'id = "newbid"')
        self.assertNotContains(response, 'id = "comment-submit"')
        self.assertNotContains(response, 'id = "add-listing-to_watchlist"')
        self.assertNotContains(response, 'id = "edit-listing"')
        self.assertNotContains(response, 'id = "end-listing-submit"')
        self.assertNotContains(response, 'id = "delete-listing"')
        self.assertNotContains(response, 'id = "winner-of-listing"')

    def test_not_active_listing_detail_page(self):
            """
            if user is Authorized but not listing's creator - display page of not active listing with full info and message that listing is ended, but without creator's manage or action interface elements: "End Listing", "Delete Listing" buttons, excluding "Show history" button
            """
            user_password_1 = "password_1"
            user_name_1 = "test_user_1"
            user_password_2 = "password_2"
            user_name_2 = "test_user_2"
            category_1_name = "category_1"

            user_1 = create_user(username = user_name_1, password = user_password_1)
            user_2 = create_user(username = user_name_2, password = user_password_2)
            category_1 = create_category(name = category_1_name)
            listing_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
            self.client.login(username = user_name_2, password = user_password_2)
            response = self.client.get(reverse("market:details", kwargs = {"listing_id":listing_active_user_1.id}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["true_user"], False)
            self.assertEqual(response.context['auctionlisting'], listing_active_user_1)
            self.assertQuerysetEqual(response.context['bids'], [])
            self.assertQuerysetEqual(response.context['comments'], [])
            self.assertEqual(response.context['bid'], None)
            self.assertContains(response, listing_active_user_1.name)
            self.assertContains(response, listing_active_user_1.description)
            self.assertContains(response, listing_active_user_1.user.username)
            self.assertContains(response, listing_active_user_1.startBid)
            self.assertContains(response, 'id = "last-price"')
            self.assertContains(response, 'id = "listing-is-ended"')
            self.assertNotContains(response, 'id = "new-bid-submit"')
            self.assertNotContains(response, 'id = "newbid"')
            self.assertNotContains(response, 'id = "comment-submit"')
            self.assertNotContains(response, 'id = "edit-listing"')
            self.assertNotContains(response, 'id = "end-listing-submit"')
            self.assertNotContains(response, 'id = "delete-listing"')
            self.assertNotContains(response, 'id = "winner-of-listing"')

    def test_not_active_listing_detail_page_creator(self):
        """
        if user is Authorized and listing's creator - display page of not active listing with full info, and message that listing is ended and full lising's manage interface elements, but without "Make bid" button
        """
        user_password_1 = "password_1"
        user_name_1 = "test_user_1"
        user_password_2 = "password_2"
        user_name_2 = "test_user_2"
        category_1_name = "category_1"

        user_1 = create_user(username = user_name_1, password = user_password_1)
        user_2 = create_user(username = user_name_2, password = user_password_2)
        category_1 = create_category(name = category_1_name)
        listing_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
        self.client.login(username = user_name_1, password = user_password_1)
        response = self.client.get(reverse("market:details", kwargs = {"listing_id":listing_active_user_1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["true_user"], True)
        self.assertEqual(response.context['auctionlisting'], listing_active_user_1)
        self.assertQuerysetEqual(response.context['bids'], [])
        self.assertQuerysetEqual(response.context['comments'], [])
        self.assertEqual(response.context['bid'], None)
        self.assertContains(response, listing_active_user_1.name)
        self.assertContains(response, listing_active_user_1.description)
        self.assertContains(response, listing_active_user_1.user.username)
        self.assertContains(response, listing_active_user_1.startBid)
        self.assertContains(response, 'id = "last-bid"')
        self.assertContains(response, 'id = "add-listing-to-watchlist"')
        self.assertContains(response, 'id = "edit-listing"')
        self.assertContains(response, 'id = "delete-listing"')
        self.assertContains(response, 'id = "last-price"')
        self.assertContains(response, 'id = "listing-is-ended"')
        self.assertNotContains(response, 'id = "new-bid-submit"')
        self.assertNotContains(response, 'id = "newbid"')
        self.assertNotContains(response, 'id = "comment-submit"')
        self.assertNotContains(response, 'id = "end-listing-submit"')
        self.assertNotContains(response, 'id = "winner-of-listing"')

    def test_not_active_listing_detail_page_user_is_winner(self):
            """
            if user is Authorized but not listing's creator and winner of that listing - display page of not active listing with full info and message that listing is ended, but without creator's manage or action interface elements: "End Listing", "Delete Listing" buttons, excluding "Show history" button
            """
            user_password_1 = "password_1"
            user_name_1 = "test_user_1"
            user_password_2 = "password_2"
            user_name_2 = "test_user_2"
            category_1_name = "category_1"

            user_1 = create_user(username = user_name_1, password = user_password_1)
            user_2 = create_user(username = user_name_2, password = user_password_2)
            category_1 = create_category(name = category_1_name)
            listing_active_user_1 = create_listing(name = "listing_1", image = "None", description = "test_desc", category = category_1, user=user_1, startBid=100, days=30, active = False)
            new_bid = Bid.objects.create(value = 150, listing = listing_active_user_1, user = user_2, date = timezone.now())
            user_2.winlist.add(listing_active_user_1)
            self.client.login(username = user_name_2, password = user_password_2)
            response = self.client.get(reverse("market:details", kwargs = {"listing_id":listing_active_user_1.id}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["true_user"], False)
            self.assertEqual(response.context['auctionlisting'], listing_active_user_1)
            self.assertQuerysetEqual(response.context['bids'], [new_bid])
            self.assertQuerysetEqual(response.context['comments'], [])
            self.assertEqual(response.context['bid'], new_bid)
            self.assertContains(response, listing_active_user_1.name)
            self.assertContains(response, listing_active_user_1.description)
            self.assertContains(response, listing_active_user_1.user.username)
            self.assertContains(response, listing_active_user_1.startBid)
            self.assertContains(response, 'id = "last-price"')
            self.assertContains(response, 'id = "listing-is-ended"')
            self.assertContains(response, 'id = "winner-of-listing"')
            self.assertNotContains(response, 'id = "new-bid-submit"')
            self.assertNotContains(response, 'id = "newbid"')
            self.assertNotContains(response, 'id = "comment-submit"')
            self.assertNotContains(response, 'id = "edit-listing"')
            self.assertNotContains(response, 'id = "end-listing-submit"')
            self.assertNotContains(response, 'id = "delete-listing"')

