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
