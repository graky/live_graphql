import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.views import GraphQLView, HttpError
from graphql.backend.core import GraphQLCoreBackend
from graphql.execution import ExecutionResult
from django.contrib.auth.models import Group, Permission, PermissionsMixin, User
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http.response import HttpResponseBadRequest
from .models import News


class NewsType(DjangoObjectType):
    class Meta:
        model = News


class NewsQuery(graphene.ObjectType):
    news_one = graphene.Field(NewsType, id=graphene.Int())
    news = graphene.List(NewsType)

    def resolve_news(self, info, **kwargs):
        return News.objects.all()

    def resolve_news_one(self, info, **kwargs):
        news_id = kwargs.get("id")
        return News.objects.get(pk=news_id)
