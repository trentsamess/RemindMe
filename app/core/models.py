from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from app.core.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=64, null=True)
    last_name = models.CharField(max_length=64, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.id}"


class Reminder(models.Model):
    creator = models.ForeignKey('User', on_delete=models.CASCADE, related_name='reminders')
    participants = models.ManyToManyField('User', blank=True)
    header = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    place = models.CharField(max_length=128, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_to_complete = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
