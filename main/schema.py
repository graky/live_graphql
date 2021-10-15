import graphene
from .mutations import Mutation
from News.subscription import BreakingNewsSubscription, CommentOnNewsSubscribe
from News.schema import NewsQuery
from User.schema import UserQuery


class Query(NewsQuery, UserQuery, graphene.ObjectType):
    ...


class Subscription(graphene.ObjectType):

    breaking_news = BreakingNewsSubscription.Field()
    comment_subscription = CommentOnNewsSubscribe.Field()


schema = graphene.Schema(
    query=Query, mutation=Mutation, subscription=Subscription, auto_camelcase=False
)
