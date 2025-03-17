from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext as _


class FriendRequestManager(models.Manager):
    def accept(self, request_id):
        """
        Принимает запрос дружбы:
        - Добавляет пользователей в друзья друг другу.
        - Удаляет сам запрос дружбы.
        """
        try:
            friend_request = self.get(id=request_id)

            from_user = friend_request.from_user
            to_user = friend_request.to_user

            if from_user == to_user:
                raise ValueError(_("Нельзя добавить самого себя в друзья."))

            from_user.friends.add(to_user)
            to_user.friends.add(from_user)

            friend_request.delete()

        except ObjectDoesNotExist:
            raise ValueError(_("Запрос дружбы с указанным ID не существует."))

    def decline(self, request_id):
        """
        Отклоняет запрос дружбы:
        - Просто удаляет запрос из базы данных.
        """
        try:
            friend_request = self.get(id=request_id)

            friend_request.delete()

        except ObjectDoesNotExist:
            raise ValueError(_("Запрос дружбы с указанным ID не существует."))
