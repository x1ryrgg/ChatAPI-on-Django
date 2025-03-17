from django.test import TestCase
from API.models import User, Message, Chat
from friend_request.models import FriendRequest


class TestClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(email='test@example.com', password='qwerty12345', username='testuser')
        cls.user2 = User.objects.create_user(email='second_test@example.com', password='qwerty12345', username='second_testuser')

    # def setUp(self):
    #     print("setUp: Run once for every test method to setup clean data.")
    #     pass

    def test_username_label(self):
        return self.assertEqual(self.user1.username, 'testuser')

    def test_set_friend(self):
        self.user1.set_friends([self.user2.pk])
        friends_list = list(self.user1.friends.all())
        expected_friends = [self.user2]

        self.assertEqual(friends_list, expected_friends)


class ChatTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(email='test@example.com', password='qwerty12345', username='testuser')
        cls.user2 = User.objects.create_user(email='second_test@example.com', password='qwerty12345', username='second_testuser')
        cls.chat = Chat.objects.create(type='direct', group_name='testgroup',creator=cls.user1)

    def test_set_members(self):
        self.chat.members.set([self.user1.pk, self.user2.pk])
        return self.assertTrue(self.chat.members.count() == 2)

    def test_members_chat(self):
        self.chat.members.set([self.user1.pk, self.user2.pk])
        members_list = list(self.chat.members.all())
        expected_members = [self.user1, self.user2]
        return self.assertEqual(members_list, expected_members)

    def test_group_name_length(self):
        max_length = self.chat._meta.get_field('group_name').max_length
        self.assertEqual(max_length, 64)


class FriendRequestTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(email='test@example.com', password='qwerty12345', username='testuser')
        cls.user2 = User.objects.create_user(email='second_test@example.com', password='qwerty12345', username='second_testuser')

        cls.request = FriendRequest.objects.create(from_user=cls.user1, to_user=cls.user2)

    def test_accept_request(self):
        FriendRequest.objects.accept(self.request.pk)

        friends_count_user1 = self.user1.friends.all().count()
        friends_count_user2 = self.user2.friends.all().count()

        self.assertEqual(friends_count_user1, 1)
        self.assertEqual(friends_count_user2, 1)

    def test_decline_request(self):
        FriendRequest.objects.decline(self.request.pk)

        friend_count_user1 = self.user1.friends.all().count()
        friend_count_user2 = self.user2.friends.all().count()

        self.assertEqual(friend_count_user1, 0)
        self.assertEqual(friend_count_user2, 0)