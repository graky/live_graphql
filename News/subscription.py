import graphene
from graphene_django import DjangoObjectType
from asgiref.sync import async_to_sync
from django.core import serializers
from channels.layers import get_channel_layer
from News.models import News, Comments

CHANNEL_LAYER = get_channel_layer()


class BreakingNewsType(DjangoObjectType):
    """Уведомление о срочной новости"""

    class Meta:
        model = News


class CommentOnNewsType(graphene.ObjectType):
    """Обновление комментариев к конкретной новости в live режиме"""

    username = graphene.String()
    comment_text = graphene.String()
    news_id = graphene.Int()


class NewsSubscription(graphene.ObjectType):

    breaking_news = graphene.Field(BreakingNewsType)
    comment_on_news = graphene.Field(CommentOnNewsType, news_id=graphene.Int())

    async def resolve_breaking_news(self, info, **kwargs):
        user = await info.context.get("user")
        channel_name = await CHANNEL_LAYER.new_channel()
        await CHANNEL_LAYER.group_add("breaking_news", channel_name)
        try:
            while user.is_authenticated:
                message = await CHANNEL_LAYER.receive(channel_name)
                yield next(serializers.deserialize("json", message["data"])).object
        finally:
            await CHANNEL_LAYER.group_discard("breaking_news", channel_name)

    async def resolve_comment_on_news(self, info, **kwargs):
        news_id = kwargs.get("news_id")
        channel_name = await CHANNEL_LAYER.new_channel()
        await CHANNEL_LAYER.group_add(str(news_id), channel_name)
        try:
            while True:
                message = await CHANNEL_LAYER.receive(channel_name)
                yield message["data"]
        finally:
            await CHANNEL_LAYER.group_discard("news_id", channel_name)
