from graphene.test import Client
from main.schema import schema
from graphql_jwt.testcases import JSONWebTokenTestCase


class TestCreateUser(JSONWebTokenTestCase):
    def test_create_user(self):
        create_user_mutation = """
            mutation Register {
                register(
                    username: "test_username"
                    password: "test_password"
                    ) {
                    user {
                        username
                        password
                    }
                }
            }
        """
        response = self.client.execute(create_user_mutation)
        self.assertIsNone(response.errors, response.errors)
        result = response.data.get("register")
        self.assertIsNotNone(result, "Doesn't get Register field")
        user = result.get("user")
        self.assertIsNotNone(user, "Doesn't get user field")
        self.assertEqual(user.get("username"), "test_username", "Not right username")
        self.assertEqual(user.get("password"), "test_password", "Not right password")
        client = Client(schema)
        response = client.execute(create_user_mutation)
        self.assertIsNone(response.get("errors"), response.get("errors"))
        result = response.get("data").get("register")
        self.assertIsNone(result, "Register field is not None")


class TestToken(JSONWebTokenTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestToken, cls).setUpClass()
        sign_in_mutation = """
                         mutation Register {
                            register(
                                username: "token_username"
                                password: "test_password"
                                ) {
                                user {
                                    username
                                    password
                                }
                            }
                        }
                    """
        client = Client(schema)
        client.execute(sign_in_mutation)
        cls.username = "token_username"
        cls.password = "password"

    def test_token(self):
        token_auth_mutation = """
            mutation TokenAuth {
                token_auth(
                    username: "token_username",
                    password: "test_password") {
                        token
                    }
                }
        """
        response = self.client.execute(token_auth_mutation)
        self.assertIsNone(response.errors, response.errors)
        result = response.data.get("token_auth")
        self.assertIsNotNone(result, "Doesn't get tokenAuth field")
        token = result.get("token")
        self.assertIsNotNone(token, "Doesn't get token")

        token_verify_mutation = """
        mutation VerifyToken {
            verify_token(
                token: "%s"
            ) {
                payload
            }
        }
        """
        token_verify_mutation %= token
        response = self.client.execute(token_verify_mutation)
        self.assertIsNone(response.errors, response.errors)
        result = response.data.get("verify_token")
        self.assertIsNotNone(result, "Doesn't get verifyToken field")
        payload = result.get("payload")
        self.assertIsNotNone(payload, "Doesn't get payload field")
        self.assertEqual(
            payload.get("username"), "token_username", "Not right username"
        )
