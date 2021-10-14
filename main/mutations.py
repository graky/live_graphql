import graphene
from News.mutations import AddNews


class Mutation(graphene.ObjectType):
    add_news = AddNews.Field()
