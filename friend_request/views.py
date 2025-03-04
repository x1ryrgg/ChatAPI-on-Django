from django.shortcuts import get_object_or_404
from rest_framework import status
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
        return FriendRequest.objects.filter(from_user=self.request.user)

    def perform_create(self, serializer):
        to_user_id = self.request.data.get('to_user')
        to_user = get_object_or_404(User, id=to_user_id)
        from_user = self.request.user

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response(
                {'error': 'Запрос дружбы уже отправлен.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if from_user == to_user:
            return Response(
                {'error': "Вы не можете отправлять запрос дружбы самому себе."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(from_user=from_user)

    def destroy(self, request, *args, **kwargs):
        to_user_id = self.request.data.get('to_user')
        friend_request = FriendRequest.objects.get(from_user=self.request.user, to_user=to_user_id)
        friend_request.delete()

        return Response({'detail': f'Запрос дружбы пользователю {to_user_id} успешно удален.'},
            status=status.HTTP_204_NO_CONTENT
                        )


class FriendResponseView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ResponseSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

    def create(self, request, *args, **kwargs):
        request_id = self.kwargs.get('request_id')
        variant = request.data.get('variant')

        if not request_id or not variant:
            return Response(
                {'error': 'Необходимо указать "request_id" и "variant".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=self.request.user)
        except FriendRequest.DoesNotExist:
            return Response(
                {'error': 'Запрос дружбы не существует или предназначен не для вас.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if variant == 1:
            new_friend = friend_request.from_user
            self.request.user.friends.add(new_friend)
            friend_request.delete()
            return Response(
                {'detail': f'Пользователь {new_friend.username} добавлен в друзья.'},
                status=status.HTTP_200_OK
            )
        elif variant == 2:
            friend_request.delete()
            return Response(
                {'detail': 'Вы отклонили запрос на добавление в друзья.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Неправильный ответ. 1 — принять; 2 — отклонить.'},
                status=status.HTTP_400_BAD_REQUEST
            )