from rest_framework import serializers
from friend_request.models import FriendRequest
from API.models import User


class RequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'created_at')
        read_only_fields =('from_user', 'created_at', 'to_user')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'created_at')
        read_only_fields = ('from_user', 'to_user', 'created_at')


