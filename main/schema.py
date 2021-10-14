import graphene
from .mutations import Mutation
from News.subscription import BreakingNewsSubscription
from News.schema import NewsQuery


class Query(NewsQuery, graphene.ObjectType):
    ...


class Subscription(graphene.ObjectType):

    on_new_chat_message = BreakingNewsSubscription.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription, auto_camelcase=False)