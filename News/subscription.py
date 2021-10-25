import channels_graphql_ws
import graphene
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


class BreakingNewsType(graphene.ObjectType):
    news_id = graphene.Int()
    news_title = graphene.String()


class CommentOnNewsType(graphene.ObjectType):
    username = graphene.String()
    comment_text = graphene.String()
    news_id = graphene.Int()


class NewsSubscription(graphene.ObjectType):
    """Срабатывает при появлении срочной новости"""

    breaking_news = graphene.Field(BreakingNewsType)
    comment_on_news = graphene.Field(CommentOnNewsType, news_id=graphene.Int())

    async def resolve_breaking_news(self, info, **kwargs):
        channel_name = await channel_layer.new_channel()
        await channel_layer.group_add("breaking_news", channel_name)
        try:
            while True:
                message = await channel_layer.receive(channel_name)
                yield message["data"]
        finally:
            await channel_layer.group_discard("breaking_news", channel_name)

    async def resolve_comment_on_news(self, info, **kwargs):
        news_id = kwargs.get("news_id")
        channel_name = await channel_layer.new_channel()
        await channel_layer.group_add(str(news_id), channel_name)
        try:
            while True:
                message = await channel_layer.receive(channel_name)
                yield message["data"]
        finally:
            await channel_layer.group_discard("news_id", channel_name)
