from django.urls import path

from . import views

app_name = 'market'

urlpatterns = [
            path('', views.IndexView.as_view(), name = 'index'),
            path('active/', views.active_listing, name = 'active'),
            path('<int:listing_id>/',views.details, name = 'details'),
            path('<int:listing_id>/comment',views.comment, name = 'comment'),
            path('categories/', views.CategoriesView.as_view(), name = 'categories'),
            path('category/<int:category_id>/listigns', views.category_listings, name = 'category_listings'),
            path('<int:listing_id>/makebid',views.makebid, name = 'makebid'),
            path('create/', views.createListing, name = 'createListing'),
            path('<int:listing_id>/edit/',views.editListing, name = 'editListing'),
            path('remove/',views.removeListing, name = 'removeListing'),
            path('endlisting/',views.endlisting, name = 'endlisting'),
            path('watchlist/',views.watchlist, name = 'watchlist'),
            path('mylistings/',views.mylistings, name = 'mylistings'),
            path('sendcontact/',views.sendcontact, name = 'sendcontact'),
            path('winlist/',views.winlistings, name = 'winlist'),
            path('mybids/',views.mybids, name = 'mybids'),
            path('inbox/',views.inbox, name = 'inbox'),
            path('chat/<int:chat_id>',views.chat, name = 'chat'),
            path('logout/', views.logout_view, name = 'logout'),
            path('login/', views.login_view, name = 'login'),
            path('signup/', views.signup, name = 'signup'),
            path('api/<int:listing_id>/last_bid', views.GetListingBidInfoView.as_view()),
        ]
