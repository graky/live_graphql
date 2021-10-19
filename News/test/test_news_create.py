from graphql_jwt.testcases import JSONWebTokenTestCase
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token
from News.models import News


class TestNewsMutation(JSONWebTokenTestCase):
    def setUp(self):
        self.user = get_user_model()(
            username="staffuser", password="test", is_staff=True
        )
        self.user.save()
        self.user2 = get_user_model()(username="notstaffuser", password="test")
        self.user2.save()
        self.token = get_token(self.user)
        self.client.authenticate(self.user)

    def tearDown(self):
        self.user.delete()
        self.user2.delete()

    def test_news_mutations_with_staff(self):
        mutation_news = """
            mutation AddNews{
                add_news(
                    text: "some text"
                    title: "News title"
                    breaking: true
                )
                {
                    message
                    success
                }
            }
        """
        response = self.client.execute(mutation_news)
        self.assertIsNone(response.errors, response.errors)
        response = response.data.get("add_news")
        self.assertEqual(response.get("message"), "News added", "News not added")
        self.assertTrue(response.get("success"), "News not added")
        news_db = News.objects.filter(
            title="News title", text="some text", breaking=True
        ).first()
        self.assertIsNotNone(news_db, "News not registred in database")

    def test_news_mutations_dublicate(self):
        mutation_news = """
                    mutation AddNews{
                        add_news(
                            text: "some text"
                            title: "Same title"
                            breaking: true
                        )
                        {
                            message
                            success
                        }
                    }
                """
        self.client.execute(mutation_news)
        mutation_news_dublicate = """
            mutation AddNews{
                add_news(
                    text: "some new text"
                    title: "Same title"
                )
                {
                    message
                    success
                }
            }
        """
        response = self.client.execute(mutation_news_dublicate)
        self.assertIsNone(response.errors, response.errors)
        response = response.data.get("add_news")

        self.assertEqual(response.get("message"), "News already exists", "News added")
        self.assertFalse(response.get("success"), "News added")
        news_db_count = News.objects.filter(title="Same title").count()
        self.assertEqual(news_db_count, 1, "More then one news with same title")

    def test_news_mutations_not_staff_user(self):
        self.client.authenticate(self.user2)
        mutation_news = """
                    mutation AddNews{
                        add_news(
                            text: "some text"
                            title: "Staff user"
                            breaking: true
                        )
                        {
                            message
                            success
                        }
                    }
                """

        response = self.client.execute(mutation_news)
        self.assertIsNone(response.errors, response.errors)
        response = response.data.get("add_news")
        self.assertEqual(response.get("message"), "User not staff", "Wrong message")
        self.assertFalse(response.get("success"), "News added")
        news_db = News.objects.filter(title="Staff user")
        self.assertFalse(news_db, "News registred in database")
