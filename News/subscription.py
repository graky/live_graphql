import graphene
from graphene_django import DjangoObjectType
from asgiref.sync import async_to_sync, sync_to_async
from django.core import serializers
from channels.layers import get_channel_layer
from News.models import News, Comments
from channels.db import database_sync_to_async

CHANNEL_LAYER = get_channel_layer()


class SubscribeNewsType(DjangoObjectType):
    """Уведомление о срочной новости"""

    class Meta:
        model = News


class CommentOnNewsType(DjangoObjectType):
    """Обновление комментариев к конкретной новости в live режиме"""

    class Meta:
        model = Comments
        fields = ["id", "text", "created_at"]

    username = graphene.String()
    news = graphene.Field(SubscribeNewsType)

    async def resolve_news(self, info, **kwargs):
        return await database_sync_to_async(lambda: self.news)()

    async def resolve_username(self, info, **kwargs):
        return await database_sync_to_async(lambda: self.user.username)()


class NewsSubscription(graphene.ObjectType):

    breaking_news = graphene.Field(SubscribeNewsType)
    comment_on_news = graphene.Field(CommentOnNewsType, news_id=graphene.Int())

    async def resolve_breaking_news(self, info, **kwargs):
        user = await info.context.get("user")
        channel_name = await CHANNEL_LAYER.new_channel()
        await CHANNEL_LAYER.group_add("breaking_news", channel_name)
        try:
            while user.is_authenticated:
                message = await CHANNEL_LAYER.receive(channel_name)
                news_id = message["news_id"]
                yield sync_to_async(News.objects.get)(pk=news_id)
        finally:
            await CHANNEL_LAYER.group_discard("breaking_news", channel_name)

    async def resolve_comment_on_news(self, info, **kwargs):
        news_id = kwargs.get("news_id")
        channel_name = await CHANNEL_LAYER.new_channel()
        await CHANNEL_LAYER.group_add(str(news_id), channel_name)
        try:
            while True:
                message = await CHANNEL_LAYER.receive(channel_name)
                comment_id = message["comment_id"]
                yield sync_to_async(Comments.objects.get)(pk=comment_id)
        finally:
            await CHANNEL_LAYER.group_discard("news_id", channel_name)
