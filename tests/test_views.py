from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from API.models import *
from API.serializers import *


class ChatsTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            email='user1@example.com',
            password='qwerty12345',
            username='user1'
        )
        cls.user2 = User.objects.create_user(
            email='user2@example.com',
            password='qwerty12345',
            username='user2'
        )
        cls.chat1 = Chat.objects.create(type='group', group_name='Chat1', creator=cls.user1)
        cls.chat1.members.add(cls.user1, cls.user2)

        cls.chat2 = Chat.objects.create(type='direct', group_name='GroupChat', creator=cls.user1)
        cls.chat2.members.add(cls.user1)

    def test_get_chats_auth_user(self):
        token = AccessToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get('')

        self.assertEqual(response.status_code, 200)

        expected_chats = ChatSerializer(Chat.objects.filter(members=self.user1).prefetch_related('members'), many=True).data
        expected_user = UserSerializer(self.user1, many=False).data

        self.assertEqual(response.data['chats'], expected_chats)
        self.assertEqual(response.data['user'], expected_user)

    def test_get_chats_unauth_user(self):
        response = self.client.get('')

        self.assertEqual(response.status_code, 401)


class ChatTests(APITestCase):
    pass