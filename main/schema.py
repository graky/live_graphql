import graphene
from .mutations import Mutation
from News.subscription import NewsSubscription
from News.schema import NewsQuery
from User.schema import UserQuery
from channels.layers import get_channel_layer


class Query(NewsQuery, UserQuery, graphene.ObjectType):
    ...


class Subscription(NewsSubscription, graphene.ObjectType):
    ...


schema = graphene.Schema(
    query=Query, mutation=Mutation, subscription=Subscription, auto_camelcase=False
)
