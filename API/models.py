from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import *


class User(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)


    def __str__(self):
        return "username: %s, email: %s, pk: %s" % (self.username, self.email, self.pk)

    def get_friends(self):
        return [friend.username for friend in self.friends.all()]

    def set_friends(self, friends):
        set_friends = []
        for friend in friends:
            friend_instance = User.objects.filter(id=friend).first()
            if friend_instance == self:
                raise ValueError("Нельзя добавлять самого себя в друзья.")
            set_friends.append(friend)

        self.friends.set(set_friends)
        return self.friends.all()


class Chat(models.Model):
    class Type(models.TextChoices):
        DIRECT = ('direct', 'директ')
        GROUP = ('group', 'группа')

    type = models.CharField(choices=Type.choices, default=Type.DIRECT, max_length=6)
    group_name = models.CharField(max_length=64, null=True, blank=True, default='noname_chat')
    members = models.ManyToManyField(User, related_name="members", blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="chat_creator")
    created_at = models.DateTimeField(auto_now_add=True)
    objects = ChatManager()

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return 'name: %s, type: %s, pk: %s' % (self.group_name, self.type, self.pk)

    def get_members(self):
        return [member.username for member in self.members.all()]


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_message")
    body = models.TextField(max_length=500, )
    created_at = models.DateTimeField(auto_now_add=True)
    objects = MessageManager()

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']

    def __str__(self):
        return 'sender: %s, message: %s' % (self.sender, self.body[:50])
