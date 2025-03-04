from rest_framework import serializers
from friend_request.models import FriendRequest


class RequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'created_at')
        read_only_fields =('from_user', 'created_at')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'created_at')
        read_only_fields = ('from_user', 'to_user', 'created_at')