import base64
import pytz
from datetime import datetime
from core.models import User
from .base import FunctionalTest

class SignupTests(FunctionalTest):

    def test_can_signup(self):
        users_at_start = User.objects.count()

        result = self.client.execute("""mutation { signup(
            email: "will@gmail.com", password: "michaelmas"
            firstName: "Will", lastName: "Parry"
        ) { token user { email firstName lastName } } }""")

        self.assertEqual(
            len(result["data"]["signup"]["token"].split(".")), 3
        )
        self.assertEqual(
            result["data"]["signup"]["user"], {
                "email": "will@gmail.com", "firstName": "Will", "lastName": "Parry"
            }
        )

        self.assertEqual(User.objects.count(), users_at_start + 1)
        self.assertNotEqual(User.objects.get(email="will@gmail.com").password, "michaelmas")
        self.assertEqual(
            User.objects.get(email="will@gmail.com").last_login,
            datetime(2000, 1, 14, 15, 0, tzinfo=pytz.UTC)
        )
    

    def test_signup_validation(self):
        users_at_start = User.objects.count()

        # Email must be unique
        self.check_query_error("""mutation { signup(
            email: "sarah@gmail.com", password: "michaelmas",
            firstName: "Will", lastName: "Parry"
        ) { token user { email firstName lastName } } }""", message="already exists")
        self.assertEqual(User.objects.count(), users_at_start)

        # Password must be 9 or more characters
        self.check_query_error("""mutation { signup(
            email: "will@gmail.com", password: "michael"
            firstName: "Will", lastName: "Parry"
        ) { token user { email firstName lastName } } }""", message="too short")
        self.assertEqual(User.objects.count(), users_at_start)

        # Password can't be numeric
        self.check_query_error("""mutation { signup(
            email: "will@gmail.com", password: "3857895787357"
            firstName: "Will", lastName: "Parry"
        ) { token user { email firstName lastName } } }""", message="numeric")
        self.assertEqual(User.objects.count(), users_at_start)

        # Password must be reasonably uncommon
        self.check_query_error("""mutation { signup(
            email: "will@gmail.com", password: "password123"
            firstName: "Will", lastName: "Parry"
        ) { token user { email firstName lastName } } }""", message="too common")
        self.assertEqual(User.objects.count(), users_at_start)



class LoginTests(FunctionalTest):

    def test_can_login(self):
        self.assertEqual(User.objects.first().last_login, None)
        result = self.client.execute("""mutation { login(
            email: "sarah@gmail.com", password: "password"
        ) { token user { email firstName lastName } } }""")

        self.assertEqual(
            len(result["data"]["login"]["token"].split(".")), 3
        )
        self.assertEqual(
            result["data"]["login"]["user"],
            {"email": "sarah@gmail.com", "firstName": "Sarah", "lastName": "Jones"}
        )
        self.assertEqual(User.objects.first().last_login, datetime(2000, 1, 14, 15, 0, tzinfo=pytz.UTC))
    

    def test_login_can_fail(self):
        self.check_query_error("""mutation { login(
            email: "sarah@gmail.com", password: "password123"
        ) { token user { email firstName lastName } } }""", message="Invalid credentials")



class UserQueryTests(FunctionalTest):

    def test_can_get_user(self):
        result = self.client.execute("""{ user { email firstName lastName } }""")
        self.assertEqual(result, {"data": {"user": {
            "email": "sarah@gmail.com", "firstName": "Sarah", "lastName": "Jones"
        }}})


    def test_root_user_is_protected(self):
        self.client.headers["Authorization"] = ""
        self.check_query_error(
            """{ user { firstName lastName } }""", message="Not authorized"
        )