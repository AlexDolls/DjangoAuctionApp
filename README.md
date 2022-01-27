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
<h2 align = "center"><strong><a href = "http://vps-39294.vps-default-host.net/market/">Try it in Live Version</a></strong></h2>
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
<hr>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/createlisting2.png">
  The listing creation process is simple, there are three fields that must be filled:
  <br><i>Name, Category, Start Price. Image and Description are optional.</i>
  <br>
  <br>When listing is created, <strong>Celery</strong> task is starting with countdown for created listing, countdown depends on the number of hours that was selected in the last field on Creation page.
  <br>
  <br><strong>Celery task:</strong><br>
  https://github.com/AlexDolls/DjangoAuctionApp/blob/0666b2d0fc0bac519a4e146953e12d79a3f89775/market/tasks.py#L14
  <br>
  <strong>Task starting with new listing creation:</strong>
  https://github.com/AlexDolls/DjangoAuctionApp/blob/0666b2d0fc0bac519a4e146953e12d79a3f89775/market/views.py#L136
  
```Python
new_listing = AuctionListing.objects.create(name = name, description = description,loaded_image=image_file,image = image, category = category, user = user, startBid = startBid, creationDate = current_date, endDate = end_date, active = active)
new_listing.save()
seconds_to_end = int(datetime.timedelta.total_seconds(new_listing.endDate - new_listing.creationDate))
task = create_task.apply_async(kwargs = {"listing_id": new_listing.id}, countdown = seconds_to_end)
```
<br>  
<h3>Index Page (Main page with all listings that exist)</h3>
<hr>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/indexpage.png">
On this page just displayed all listings that currently exist with main info about them in boxes.
There are opportunity to show only Active, yours or with special Category listings.
<br>
<br>
<h3>Detail Listing's page</h3>
<hr>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/listing2.png">
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/listing2_1.png">
All information about listing displayed on it's detail page:
<br><i>Name, image, price, last bid, time to end <strong>(JS live timer)</strong> and Owner</i>
<br>
<br><strong>Websocket</strong> connection automatically opens with anyone, who entered on this page. (separed connection groups for each listing). Websocket connection makes "live" <strong>bid</strong> system and comments.
<br>
https://github.com/AlexDolls/DjangoAuctionApp/blob/f8f678442d88b397c10aa1a1e0df40a8ab5700bd/market/consumers.py#L22

```Python
class ListingConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['listing_id']
        self.room_group_name = 'market_%s' % self.room_name

        #Join room group by listing url
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
            )
        self.accept()
```
<br>
<h3>Inbox and Chat</h3>
<hr>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/inbox.png">
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/chat.png">
On inbox page you can enter to chat that exists between you and other user, or you can create new chat, but only if you haven't chat created with target user already.
<br>
<br><strong>Websocket</strong> connection for chat system is active on every page and only for Authorized user's.
<br>
<i>Every Authorized user connects to websocket on <strong>Chat Consumer</strong> and have it's own "connection group" with himself only. It's safety, cause only target user will get websocket message on his client and there are still posible to show new messages count in 'live' with Inbox NavBar menu</small></i>
<br>
https://github.com/AlexDolls/DjangoAuctionApp/blob/f8f678442d88b397c10aa1a1e0df40a8ab5700bd/market/consumers.py#L222

```Python
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if self.user.is_active == True and self.user.is_anonymous == False:
            self.room_group_name = f'chat_{self.user.id}'

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()
        else:
            self.close()

```
<br>
<h3>User Cabinet</h3>
<hr>
<img src = "https://github.com/AlexDolls/DjangoAuctionApp/blob/master/screenshots_readme/usercabinet.png">
It is simple user's cabinet, where possible to see main information about User.
<br>There are also opportunity to change user's Avatar. Using template Django form and <strong>Pillow</strong> allow to save media files in safety way. (To make sure that is really media files)
<br>
<h2>Installation</h2>
<h3>Basic requirements</h3>
Install <a href = "https://docs.docker.com/get-docker/"><strong>Docker Engine</strong></a> and <a href = "https://docs.docker.com/compose/install/"><strong>Docker Compose</strong></a> on your PC.
<h3>Development</h3>

1. Rename *.env.dev-sample* to *.env.dev*.
1. Update the environment variables in the *docker-compose.yml* and *.env.dev* files.
1. Build the images and run the containers:

    ```bash
    $ docker-compose up -d --build
    ```
1. Don't forget to create superuser (needs to get access to admin panel)

    ```bash
    $ docker-compose exec web python3 manage.py createsuperuser
    ```

 Test it out at [http://localhost:8000](http://localhost:8000)(http://127.0.0.1:8000).
<h3>Production</h3>
Uses daphne + nginx.

1. Rename *.env.prod-sample* to *.env.prod* and *.env.prod.db-sample* to *.env.prod.db*. Update the environment variables as you need.
1. Build the images and run the containers:

    ```sh
    $ docker-compose -f docker-compose.prod.yml up -d --build
    ```
1. Make migartions to DB

    ```sh
    $ docker-compose -f docker-compose.prod.yml exec web python3 manage.py makemigrations
    $ docker-compose -f docker-compose.prod.yml exec web python3 manage.py migrate
    ```
    
1. Collect staticfiles
    
    ```sh
    $ docker-compose -f docker-compose.prod.yml exec web python3 manage.py collectstatic
    ``` 
1. Don't forget to create superuser (needs to get access to admin panel)

    ```bash
    $ docker-compose exec web python3 manage.py createsuperuser
    ```
    
<h3>Autotests</h3>
It's nice practice to run tests before and after making some changes and before deploying.
Major part of project's fucntions are covered by autotests, to <strong>run</strong> it execute command below:
<h4>Development</h4>

```bash
$ docker-compose exec web pytest
```
 <h4>Production</h4>
 
   ```bash
   $ docker-compose -f docker-compose.prod.yml exec web pytest
   ```
 
Test it out at [http://localhost:1337](http://localhost:1337)(http://127.0.0.1:1337). To apply changes, the image must be re-built.
