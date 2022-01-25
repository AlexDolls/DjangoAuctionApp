<h1 align="center">DjangoAuctionApp</h1>
<p align = "center">
<a href = "https://github.com/django/django"><img src = "https://img.shields.io/badge/Django-3.2.9-green"></img></a>
<a href ="https://www.python.org/downloads/release/python-397/"><img src = "https://img.shields.io/badge/Python-3.9.7-green"></img></a>
<a href = "https://www.django-rest-framework.org/"><img src = "https://img.shields.io/badge/DRF-3.12.4-red"></img></a>
<a href = "https://github.com/django/channels"><img src = "https://img.shields.io/badge/DjangoChannels-3.0.4-blue"></img></a>
<a href = "https://github.com/celery/celery"><img src = "https://img.shields.io/badge/Celery-5.2.3-light%20green"></img></a>
</p>
<p align = center>
<img src = "https://i.imgur.com/WoLMzyU.png"><img>
<h2 align = "center"><strong><a href = "#">Try it in Live Version</a></strong></h2>
</p>
<h2>Technologies used in project</h2>
<ol>
<li><strong>Python3</strong></li>
<li><strong>Django3</strong></li>
<li><strong>DRF (Django Rest Framework)</strong> - <i>getting actual info by using REST (in this project by AJAX on frontend)</i></li>
<li><strong>Django Channels</strong> - <i>websocket connection for bid system and chat</i></li>
<li><strong>Celery</strong> - <i>automatic listing's completion by task with countdown</i></li>
<li><strong>Docker</strong> - <i>project deploying (dev and prod deploying versions)</i></li>
</ol>
<h2>Description</h2>
<h3>Listing Creation</h3>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/createlisting2.png">
  The listing creation process is simple, there are three fields that must be filled - Name, Category and Start Price. Image and Description are optional.
  <br>When listing is created, <strong>Celery</strong> task is starting with countdown for created listing, countdown depends on the number of hours that was selected in the last field on Creation page.
<hr>
<h3>Index Page (Main page with all listings that exist)</h3>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/indexpage.png">
On this page just displayed all listings that currently exist with main info about them in boxes.
There are opportunity to show only Active, yours or with special Category listings.
<hr>
<h3>Detail Listing's page</h3>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/listing2.png">
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/listing2_1.png">
All information about listing displayed on it's detail page.
<br><strong>Websocket</strong> connection automatically opens with anyone, who entered on this page. (separed connection groups for each listing). Websocket connection makes "live" <strong>bid</strong> system and comments.
<hr>
<h3>Inbox and Chat</h3>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/inbox.png">
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/chat.png">
On inbox page you can enter to chat that exists between you and other user, or you can create new chat, but only if you haven't chat created with target user already.
<br><strong>Websocket</strong> connection for chat system is active on every page and only for Authorized user's.
<br><i style = "color:gray">Every Authorized user connects to websocket on Chat Consumer and have it's own "connection group" with himself only. It's safety, cause only target user will get websocket message on his client and there are still posible to show new messages count in 'live' with Inbox NavBar menu</i>
<hr>
<h3>User Cabinet</h3>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/usercabinet.png">
It is simple user's cabinet, where possible to see main information about User.
<br>There are also opportunity to change user's Avatar. Using template Django form and Pillow allow to save media files in safety way. (To make sure that is really media files)
