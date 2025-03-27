from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from API.models import Chat


class IsMemberOfChat(permissions.BasePermission):
    """
    Резрешение, которое позволяет использовать ресурс только участникам чата.
    """
    message = 'Вы не являетесь участником этого чата.'

    def has_permission(self, request, view):
        id = view.kwargs.get('id')
        if id:
            chat = get_object_or_404(Chat, id=id)
            if request.user not in chat.members.all():
                return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user not in obj.members.all():
            return False
        return True

