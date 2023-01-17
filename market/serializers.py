from rest_framework import serializers

from .models import Bid


class BidUserSerializer(serializers.Serializer):
    username = serializers.CharField(source='user.username', max_length=200)
    user_id = serializers.IntegerField(source="user.id")


class BidSerializer(serializers.ModelSerializer):
    user = BidUserSerializer(source="*")

    class Meta:
        model = Bid
        fields = ['date', 'user', 'value']
    # date = serializers.DateTimeField()
    # user = serializers.CharField(source = 'user.username', max_length = 200)
    # value = serializers.DecimalField(decimal_places = 2, max_digits = 7)
    # name = serializers.CharField(max_length=32)
    # image = serializers.URLField(allow_blank=True)
    # description = serializers.CharField(max_length = 150)
    # startBid = serializers.DecimalField(decimal_places = 2, max_digits = 7)
    # creationDate = serializers.DateTimeField()
    # endDate = serializers.DateTimeField()
    # active = serializers.BooleanField()
