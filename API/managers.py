from django.contrib.auth.base_user import BaseUserManager
from .models import *
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):

    def create_user(self, username: str = None, password=None, email=None, **extra_fields):
        if email is None:
            raise ValueError('email must be set')

        if username is None:
            username = email

        email = self.normalize_email(email)
        user =self.model(username=username, email=email, password=password, **extra_fields)
        user.save()
        logger.info('Created new user "%s"' % username)
        return user

    def create_superuser(self, email, password=None, username: str = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.create_user(email, password, username, **extra_fields)
        logger.info('Created new superuser "%s"' % username)
        return user


class ChatManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        logger.info('Created new groupchat "%s"' % obj)
        return obj


class MessageManager(models.Manager):
    def create(self, **kwargs):
        obj = self.model(**kwargs)
        obj.save()
        logger.info('Created new groupchat "%s"' % obj)
        return obj