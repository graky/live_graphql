import django.contrib.auth
import graphene
from django.contrib.auth.models import User
from graphene_django.types import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = User


class UserQuery(graphene.ObjectType):
    user = graphene.Field(UserType)

    def resolve_user(self, info):
        if info.context.user.is_authenticated:
            return info.context.user
        return None