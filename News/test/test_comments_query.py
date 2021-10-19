from graphql_jwt.testcases import JSONWebTokenTestCase
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token
from News.models import News, Comments


class TestCommentsQuery(JSONWebTokenTestCase):
    def setUp(self):
        self.user = get_user_model()(username="comments", password="test")
        self.user.save()
        self.token = get_token(self.user)
        self.client.authenticate(self.user)
        self.news1 = News.objects.create(
            title="Тестовая новость с комментариями", text="Описание тестовой новости"
        )
        self.comments = Comments.objects.create(
            user=self.user, news=self.news1, text="Текст комментария"
        )
        self.comments2 = Comments.objects.create(
            user=self.user, news=self.news1, text="Текст комментария2"
        )

    def tearDown(self):
        self.user.delete()
        self.news1.delete()
        self.comments.delete()
        self.comments2.delete()

    def test_comments_query(self):
        query_comments = """
            query Comments{
                comments(news_id:%s){
                    user{
                        username
                    }
                    text
                }
            }
        """
        query_comments %= self.news1.id
        response = self.client.execute(query_comments)
        self.assertIsNone(response.errors, response.errors)
        response = response.data.get("comments")
        comments_db = [
            {"user": {"username": "comments"}, "text": "Текст комментария"},
            {"user": {"username": "comments"}, "text": "Текст комментария2"},
        ]
        self.assertEqual(response, comments_db, "Not right comments list")
