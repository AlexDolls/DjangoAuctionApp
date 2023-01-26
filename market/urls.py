from django.urls import path

from .views import *

app_name = 'market'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('active/', active_listing, name='active'),
    path('<int:listing_id>/', details, name='details'),
    path('<int:listing_id>/comment', comment, name='comment'),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('category/<int:category_id>/listings', category_listings, name='category_listings'),
    path('<int:listing_id>/makebid', makebid, name='makebid'),
    path('create/', createListing, name='createListing'),
    path('<int:listing_id>/edit/', editListing, name='editListing'),
    path('remove/', removeListing, name='removeListing'),
    path('watchlist/', watchlist, name='watchlist'),
    path('mylistings/', mylistings, name='mylistings'),
    path('sendcontact/', sendcontact, name='sendcontact'),
    path('winlist/', winlistings, name='winlist'),
    path('mybids/', mybids, name='mybids'),

    path('inbox/', Inbox.as_view(), name='inbox'),
    path('inbox/<int:chat_id>', Inbox.as_view(), name='chat'),

    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('user/<int:user_id>', add_user_avatar, name="add_user_avatar"),
    path('signup/', signup, name='signup'),
    path('api/<int:listing_id>/last_bid', GetListingBidInfoView.as_view()),
    path('api/<int:listing_id>/all_bids', GetListingBidsTotalInfoView.as_view()),
    path('task/<task_id>', get_status, name="get_task_status"),
]
