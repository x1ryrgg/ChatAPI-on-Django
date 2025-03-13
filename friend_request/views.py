from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


from API.models import User
from friend_request.models import FriendRequest
from friend_request.serializers import *


class FriendRequestView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        """
        Просмотр запросов, которые отправил пользователь
        url: /requests/
        """
        return FriendRequest.objects.filter(from_user=self.request.user)

    def perform_create(self, serializer):
        """
        Отправка запроса на добавление в друзья
        url: /requests/
        body: to_user (int)
        """
        to_user_id = self.request.data.get('to_user')
        to_user = get_object_or_404(User, id=to_user_id)
        from_user = self.request.user

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response(_('Запрос уже отправлен.'))

        if from_user == to_user:
            return Response(_("Вы не можете отправлять запрос дружбы самому себе."), status=status.HTTP_400_BAD_REQUEST)

        serializer.save(from_user=from_user)

    def destroy(self, request, *args, **kwargs):
        """
        Удаление запроса
        url: /requests/
        body: to_user (int)
        """
        to_user_id = self.request.data.get('to_user')
        friend_request = FriendRequest.objects.get(from_user=self.request.user, to_user=to_user_id)
        friend_request.delete()

        return Response(_(f'Запрос дружбы пользователю {to_user_id} успешно удален.'))

    @action(methods=['get'],
            detail=False,
            url_path='check')
    def check_users(self, request):
        """
        Для просмотра пользователей (которых нет в друзьях)
        url: /requests/check/
        """
        friends = request.user.friends.all()
        query = User.objects.exclude(id__in=friends.values_list('id', flat=True))
        serializer = UserSeralizer(query, many=True)
        return Response(serializer.data)


class FriendResponseView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ResponseSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        """
        Просмотр запросов пользователю
        url: /responses/
        """
        return FriendRequest.objects.filter(to_user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Варианты ответа на запрос (1 - добавить в друзья; 2 - отклонить запрос)
        url: /responses/request_id/
        body: choise (int)
        """
        request_id = self.kwargs.get('request_id')
        choise = request.data.get('variant')

        if not request_id or not choise:
            return Response(_('Необходимо указать "request_id" и "variant".'))

        try:
            friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=self.request.user)
        except FriendRequest.DoesNotExist:
            return Response(_('Запрос дружбы не существует или предназначен не для вас.'))

        if choise == 1:
            new_friend = friend_request.from_user
            self.request.user.friends.add(new_friend)
            friend_request.delete()
            return Response(_(f'Пользователь {new_friend.username} добавлен в друзья.'), status=status.HTTP_200_OK)
        elif choise == 2:
            friend_request.delete()
            return Response(_('Запрос на добавление в друзья отклонен.'), status=status.HTTP_200_OK)
        else:
            raise ValidationError(_('Неправильный ответ. 1 — принять; 2 — отклонить.'))


class FriendsViewSet(ModelViewSet):
    serializer_class = UserSeralizer
    http_method_names = ['get', 'delete']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends.all()

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=pk)
        request.user.friends.remove(user)
        return Response(_(f"{user} успешно удален из друзей."))