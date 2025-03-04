from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import *


class User(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return f"{self.username}, {self.email}, pk {self.pk}"


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
        return f'Name: {self.group_name}, pk: {self.pk}, type: {self.type}'


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
        return f'Sender {self.sender} | message {self.body[:50]} '
