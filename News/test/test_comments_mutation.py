from graphql_jwt.testcases import JSONWebTokenTestCase
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token
from News.models import News, Comments


class TestCommentsMutation(JSONWebTokenTestCase):
    def setUp(self):
        self.user = get_user_model()(username="commentsuser", password="test")
        self.user.save()
        self.token = get_token(self.user)
        self.client.authenticate(self.user)
        self.news1 = News.objects.create(
            title="Новость для комментариев", text="Описание тестовой новости"
        )

    def tearDown(self):
        self.user.delete()
        self.news1.delete()

    def test_comments_mutations(self):
        mutation_comments = """
            mutation AddComents{
                add_comment(
                    news_id:%s,
                    text: "Комментарий к новости"
                    )
                    {
                        message
                        success
                    }
                }
        """
        mutation_comments %= self.news1.id
        response = self.client.execute(mutation_comments)
        self.assertIsNone(response.errors, response.errors)
        response = response.data.get("add_comment")
        self.assertEqual(response.get("message"), "comment added", "Comment not added")
        self.assertTrue(response.get("success"), "Comment not added")
        comments_db = Comments.objects.filter(
            user=self.user, news=self.news1, text="Комментарий к новости"
        ).first()
        self.assertIsNotNone(comments_db, "Comment not registred in database")
