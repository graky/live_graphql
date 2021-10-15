import channels_graphql_ws
import graphene


class BreakingNewsSubscription(channels_graphql_ws.Subscription):
    """Срабатывает при появлении срочной новости"""

    news_id = graphene.Int()
    news_title = graphene.String()

    def subscribe(self, info):
        return None

    def publish(self, info):

        news_id = self["news_id"]
        news_title = self["news_title"]

        return BreakingNewsSubscription(
            news_id=news_id,
            news_title=news_title,
        )

    @classmethod
    def deliver_news(cls, news_title, news_id):
         cls.broadcast(
            payload={"news_title": news_title, "news_id": news_id},
        )


class CommentOnNewsSubscribe(channels_graphql_ws.Subscription):
    """Срабатывает при появлении комментария на новость, на которую подписан пользователь"""

    username = graphene.String()
    comment_text = graphene.String()
    news_id = graphene.Int()

    class Arguments:

        news_id = graphene.Int()

    def subscribe(self, info, news_id):
        return [str(news_id)]

    def publish(self, info, news_id):

        username = self["username"]
        comment_text = self["text"]

        return CommentOnNewsSubscribe(
            news_id=news_id,
            comment_text=comment_text,
            username=username,
        )

    @classmethod
    def comment_notify(cls, news_id, username, text):
         cls.broadcast(
             group=news_id,
            payload={"username": username, "text": text},
        )