import graphene
from .schema import UserType
from django.contrib.auth.models import User


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