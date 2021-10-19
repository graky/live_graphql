from graphql_jwt.testcases import JSONWebTokenTestCase
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token
from News.models import News


class TestNewsQuery(JSONWebTokenTestCase):
    def setUp(self):
        self.user = get_user_model()(username="test1", password="test")
        self.user.save()
        self.token = get_token(self.user)
        self.client.authenticate(self.user)
        self.news1 = News.objects.create(
            title="Тестовая новость", text="Описание тестовой новости"
        )
        self.news2 = News.objects.create(
            title="Тестовая новость2", text="Описание тестовой новости2", breaking=True
        )

    def tearDown(self):
        self.user.delete()
        self.news1.delete()
        self.news2.delete()

    def test_query_news(self):
        query_news = """
            query News{
                news{
                    id
                    text
                    title
                    breaking
                }
            }
        """
        response = self.client.execute(query_news)
        self.assertIsNone(response.errors, response.errors)
        response = response.data.get("news")
        self.assertEqual(len(response), 2, "Not two news objects")
        news_db = [
            {
                "id": str(self.news2.id),
                "title": "Тестовая новость2",
                "text": "Описание тестовой новости2",
                "breaking": True,
            },
            {
                "id": str(self.news1.id),
                "title": "Тестовая новость",
                "text": "Описание тестовой новости",
                "breaking": False,
            },
        ]
        self.assertEqual(response, news_db, "Not right list of news objects")

    def test_query_news_one(self):
        query_news = """
            query News{
                news_one(id:%s){
                    id
                    text
                    title
                    breaking
                }
            }
        """
        query_news %= self.news2.id
        response = self.client.execute(query_news)
        self.assertIsNone(response.errors, response.errors)
        response = response.data.get("news_one")
        news_object = {
            "id": str(self.news2.id),
            "title": "Тестовая новость2",
            "text": "Описание тестовой новости2",
            "breaking": True,
        }
        self.assertEqual(response, news_object, "Not right  news object")
