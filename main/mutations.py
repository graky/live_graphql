import graphene
import graphql_jwt
from News.mutations import AddNews, AddComment
from User.mutations import Register


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    add_news = AddNews.Field()
    register = Register.Field()
    add_comment = AddComment.Field()
