from django.contrib.auth.base_user import BaseUserManager
from .models import *
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):

    def get_queryset(self):
        return super().get_queryset()

    def create_user(self,  email, password=None, username: str = None, **extra_fields):
        """
        Creates and saves User with the given email and password
        """

        if not email:
            raise ValueError("The email field is required")

        if username is None:
            username = email

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        logger.info("%s user, base folders and 'Favorites' room are created" % user)
        return user

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        """
        Creates and saves superuser with the given email and password
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.create_user(email, username, password, **extra_fields)
        logger.info("%s superuser created" % user)
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