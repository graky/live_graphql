import graphene
import graphql_jwt
import channels.auth
from .schema import UserType
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


class Register(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        username = kwargs.get("username")
        password = kwargs.get("password")
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "password": password,
            },
        )
        if created:
            return Register(user=user)


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)
    session = graphene.String()

    @classmethod
    def resolve(cls, root, info, **kwargs):
        user = info.context.user
        if user:
            channels.auth.login(info.context, user)
            info.context.session.save()

            if info.context.session.session_key:
                # print(session.session_key)
                return cls(user=user, session=info.context.session.session_key)
            else:
                raise Exception("try it again")
