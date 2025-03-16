from django.db import models
from django.urls import reverse

from API.models import User


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='from_request', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_request', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}'


