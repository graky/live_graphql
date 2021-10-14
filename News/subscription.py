import channels_graphql_ws
import graphene


class BreakingNewsSubscription(channels_graphql_ws.Subscription):
    """Subscription triggers on a new chat message."""

    news_id = graphene.Int()
    news_title = graphene.String()

    def subscribe(self, info):
        return None

    def publish(self, info, chatroom=None):

        news_id = self["news_id"]
        news_title = self["news_title"]

        return BreakingNewsSubscription(
            news_id=news_id, news_title=news_title,
        )

    @classmethod
    def deliver_news(cls, news_title, news_id):
        cls.broadcast(
            payload={"news_title": news_title, "news_id": news_id},
        )