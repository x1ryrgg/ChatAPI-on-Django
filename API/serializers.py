from adrf import serializers as async_serializers
from rest_framework import serializers

from API.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Message
        fields = ('pk', 'chat', 'sender', 'body', 'created_at',)
        read_only_fields = ('sender', 'created_at', 'chat')


class ChatSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'type', 'group_name', 'members', 'creator', 'created_at', 'messages')
        read_only_fields = ('creator', 'created_at')


class ChatUserControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'type', 'group_name', 'members', 'creator', 'created_at')
        read_only_fields = ('creator', 'created_at')


class AsyncMessageSerializer(async_serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('pk', 'chat', 'sender', 'body', 'created_at',)
        read_only_fields = ['sender', 'created_at', 'chat']
