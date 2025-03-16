from django.test import TestCase
from API.models import User, Message, Chat

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







