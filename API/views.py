import asyncio

from asgiref.sync import sync_to_async
from rest_framework.viewsets import ModelViewSet
from adrf.viewsets import ModelViewSet as AsyncModelViewSet
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

from . import permissions
from .models import *
from .permissions import IsMemberOfChat
from .serializers import *
from .tasks import add_numbers


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        """
        Регистрация пользователя
        url: /register/
        body: username (str), password (str), email (str)
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class User(ModelViewSet):
    """
    Список пользователей
    url: /user/
    """
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='mutual')
    def mutual_friends(self, request, *args, **kwargs):
        current_user = request.user
        other_user = self.get_object()

        common_friends = current_user.friends.filter(friends=other_user).distinct()
        serializer = UserSerializer(common_friends, many=True)
        if common_friends:
            return Response(serializer.data)
        return Response(_("У вас нет общих друзей."))


class ChatAPIView(ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOfChat]
    serializer_class = ChatSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        user = self.request.user
        chats_query = Chat.objects.filter(members=user).prefetch_related('members')
        return chats_query

    def list(self, request, *args, **kwargs):
        """
        Все чаты, в которых присутствует пользователь
        url: /index/
        """
        user = request.user
        user_data = UserSerializer(user, many=False)

        chats_data_key = f'chatgroup_data_{user.username}'
        chats_data = cache.get(chats_data_key)
        if not chats_data:
            chats_query = Chat.objects.filter(members=user).prefetch_related('members')
            chats_data = ChatSerializer(chats_query, many=True).data
            cache.set(chats_data_key, chats_data, 60)

        data = {
            'user': user_data.data,
            'chats': chats_data
        }

        return Response(data)

    def perform_create(self, serializer):
        """
        Создание чата
        url: /index/
        body {
            group_name (str), members (list)
        }
        """
        members_data = self.request.data.get('members', [])

        members = []
        for user_id in members_data:
            user = get_object_or_404(User, id=user_id)
            members.append(user)

        for member in members:
            if member not in self.request.user.friends.all():
                raise serializers.ValidationError(_("Вы можете добавлять только своих друзей."))

        total_members = len(members) + 1
        chat_type = 'direct' if total_members <= 2 else 'group'

        chat = serializer.save(
            creator=self.request.user,
            type=chat_type
        )
        chat.members.set([self.request.user] + list(members))

    def retrieve(self, request, *args, **kwargs):
        """
        Просмотр чата и его сообщений
        url: /index/chat_id/
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Удаление чата
        url: /index/chat_id/
        """
        instance = self.get_object()

        if instance.creator != self.request.user:
            raise permissions.PermissionDenied(_("Только создатель чата может его удалять."))

        self.perform_destroy(instance)
        return Response(_(f"Чат {instance.group_name} успешно удален."))

    @action(methods=['get'], detail=True, url_path='stats')
    def stats(self, request, *args, **kwargs):
        """
        Просмотр статистики чата
        url: /index/chat_id/stats/
        """
        chat = self.get_object()
        stata = {
            'total_members': chat.members.count(),
            'total_messages': chat.messages.count(),
            "last_message": chat.messages.order_by('-created_at').first(),
            'last_message_date': chat.messages.order_by('-created_at').first().created_at if chat.messages.exists() else None,
        }
        serializer = ChatStatsSerializer(stata)
        if request.user != chat.creator:
            raise PermissionDenied(_('Только создатель чата может просматривать статистику чата'))

        return Response(serializer.data)


class MessageApiView(ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOfChat]
    serializer_class = MessageSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        """
        Сообщения в конкретном чате
        url: chat/chat_id/messages/
        """
        chat_id = self.kwargs.get('id')
        return Message.objects.filter(chat_id=chat_id).select_related('chat', 'sender')

    def perform_create(self, serializer):
        """
        Добавление сообщения в чат
        url: chat/chat_id/messages/
        body: body (str)
        """
        chat_id = self.kwargs.get('id')
        chat = get_object_or_404(Chat, id=chat_id)
        serializer.save(chat=chat)

    def retrieve(self, request, *args, **kwargs):
        """
        Данные об конкретном сообщении из чата
        url: chat/chat_id/messages/message_id/
        """
        message_id = kwargs.get('message_id')
        message = get_object_or_404(Message, id=message_id)
        serializer = MessageSerializer(message, many=False)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Удаление сообщения из чата
        url: chat/chat_id/messages/message_id/
        """
        message_id = kwargs.get('message_id')
        message = get_object_or_404(Message, id=message_id)

        if message.sender != self.request.user:
            return Response(_('Нет прав на на удаление этого объекта'))

        self.perform_destroy(message)
        return Response(_('сообщение успешно удалено.'))


class ChatUserControlView(ModelViewSet):
    permission_classes = [IsAuthenticated, IsMemberOfChat]
    serializer_class = ChatUserControlSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'chat_id'
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        """
        Данные о чате
        url: /chat/chat_id>/peer/
        """
        chat_id = self.kwargs.get('id')
        return Chat.objects.filter(id=chat_id)

    def partial_update(self, request, *args, **kwargs):
        """
        Добавление друзей в чат
        url: chat/chat_id/peer/
        body: members (list)
        """
        chat_id = self.kwargs.get('id')
        chat = get_object_or_404(Chat, pk=chat_id)

        if request.user != chat.creator:
            raise serializers.ValidationError(_('Только создатель чата может приглашать новых участников.'))

        members_data = request.data.get('members', [])
        members_to_add = []
        for user_id in members_data:
            user = get_object_or_404(User, id=user_id)
            members_to_add.append(user)

        invalid_users = [user.id for user in members_to_add if user not in self.request.user.friends.all()]
        if invalid_users:
            raise ValidationError(_(f"Вы можете добавлять только своих друзей. Недопустимые ID: {invalid_users}"))

        chat.members.add(*members_to_add)
        return Response(_(f"Пользоваетль {members_to_add} был добавлен в чат."))

    def remove_members(self, request, *args, **kwargs):
        """
        Удаление пользователей из чата
        url: chat/chat_id/peer/
        body: members (list)
        """
        chat_id = self.kwargs.get('id')
        chat = get_object_or_404(Chat, pk=chat_id)

        if request.user != chat.creator:
            raise serializers.ValidationError(_("Только создатель чата может удалять участников."))

        members_data = request.data.get('members', [])
        members_to_remove = []
        for user_id in members_data:
            user = get_object_or_404(User, id=user_id)
            members_to_remove.append(user)

        invalid_users = [user.id for user in members_to_remove if user not in chat.members.all()]
        if invalid_users:
            raise ValidationError(_(f"Вы можете удалять тех, кого нет в чате. Недопустимые ID: {invalid_users}"))

        chat.members.remove(*members_to_remove)
        return Response(_(f"Пользователь {members_to_remove} был удален из чата."))


class MessageViewSet(AsyncModelViewSet):
    queryset = Message.objects.all()
    serializer_class = AsyncMessageSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=False, url_path='async-sendes')
    async def async_my_sends(self, request, *args, **kwargs):
        query = await sync_to_async(list)(self.get_queryset().filter(sender=request.user))
        # Сериализация данных
        serializer = self.get_serializer(query, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='sendes')
    def my_sends(self, request, *args, **kwargs):
        query = self.get_queryset().filter(sender=self.request.user)
        serializer = MessageSerializer(query,many=True)
        return Response(serializer.data)


class CeleryTest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            add_numbers.delay(10, 20)
            return Response(_("Celery task has been complete"))
        except Exception as e:
            return Response(str(e))