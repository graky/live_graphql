from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class SettingsBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.get(username=username)
        if user.password == password:
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
