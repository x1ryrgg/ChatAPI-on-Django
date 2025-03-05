from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Создаем нового пользователя
            refresh = RefreshToken.for_user(user)  # Генерируем токены
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def users(request):
#     user = User.objects.all()
#     serializer = UserSerializer(user, many=True)
#
#     return Response(serializer.data)
#

class user(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ChatsView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        """ Информация о пользователе и о чатах, в которых он присутствует """
        user = request.user

        chats = Chat.objects.filter(members=user).prefetch_related('members')

        context = {
            'user': UserSerializer(user).data,
            'chats': ChatSerializer(chats, many=True).data,
        }

        return Response(context)


# class ChatCreateView(generics.CreateAPIView):
#
#     queryset = Chat.objects.all()
#     serializer_class = ChatSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(creator=self.request.user)
#         chat = serializer.save(creator=self.request.user)
#         chat.members.add(self.request.user)

class ChatAPIView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        """ Все чаты, в которых присутствует пользователь """
        return Chat.objects.filter(members=self.request.user).prefetch_related('members')

    def perform_create(self, serializer):
        """ Создание чата """
        members_data = self.request.data.get('members', [])

        members = []
        for user_id in members_data:
            user = get_object_or_404(User, id=user_id)
            members.append(user)

        for member in members:
            if member not in self.request.user.friends.all():
                raise serializers.ValidationError("Вы можете добавлять только своих друзей.")

        chat = serializer.save(creator=self.request.user)
        chat.members.add(self.request.user)
        chat.members.add(*members)


class MessageApiView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'delete', 'put']

    def get_queryset(self):
        """ Сообщения в конкретном чате """
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)

        if self.request.user not in chat.members.all():
            return Message.objects.none()

        return Message.objects.filter(chat_id=chat_id).select_related('chat', 'sender')

    def perform_create(self, serializer):
        """ Добавление сообщения в чат """
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)

        if self.request.user not in chat.members.all():
            return Response(
                {'error': 'Вы не являетесь участником этого чата.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save(chat=chat)

    def retrieve(self, request, *args, **kwargs):
        """ Данные об конкретном сообщении из чата """
        instance = self.get_object()

        if request.user not in instance.chat.members.all():
            return Response(
                {'error': 'У вас нет прав на просмотр этого сообщения.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """ Удаление сообщения из чата """
        instance = self.get_object()

        if instance.sender != self.request.user:
            return Response(
                {'error': 'Нет прав на на удаление этого объекта'},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(
            {'detail': 'сообщение успешно удалено.'},
            status=status.HTTP_204_NO_CONTENT)


class ChatUserControlView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'chat_id'
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        """ Данные о чате """
        chat_id = self.kwargs.get('chat_id')
        return Chat.objects.filter(id=chat_id)

    def partial_update(self, request, *args, **kwargs):
        """ Добавление друзей в чат """
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, pk=chat_id)

        if request.user != chat.creator:
            raise serializers.ValidationError('Только создатель чата может приглашать новых участников.')

        members_data = request.data.get('members', [])
        members_to_add = []
        for user_id in members_data:
            user = get_object_or_404(User, id=user_id)
            members_to_add.append(user)

        invalid_users = [user.id for user in members_to_add if user not in self.request.user.friends.all()]
        if invalid_users:
            raise ValidationError(f"Вы можете добавлять только своих друзей. Недопустимые ID: {invalid_users}")

        chat.members.add(*members_to_add)
        return Response(f"Пользоваетль {members_to_add} был добавлен в чат.")

    def remove_members(self, request, *args, **kwargs):
        """ Удаление пользователей из чата """
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, pk=chat_id)

        if request.user != chat.creator:
            raise serializers.ValidationError("Только создатель чата может удалять участников.")

        members_data = request.data.get('members', [])
        members_to_remove = []
        for user_id in members_data:
            user = get_object_or_404(User, id=user_id)
            members_to_remove.append(user)

        invalid_users = [user.id for user in members_to_remove if user not in chat.members.all()]
        if invalid_users:
            raise ValidationError(f"Вы можете удалять тех, кого нет в чате. Недопустимые ID: {invalid_users}")

        chat.members.remove(*members_to_remove)
        return Response(f"Пользователь {members_to_remove} был удален из чата.")