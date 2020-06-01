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
        result = self.client.execute("""{ user {
            email firstName lastName timezone dayEnds
        } }""")
        self.assertEqual(result, {"data": {"user": {
            "email": "sarah@gmail.com", "firstName": "Sarah",
            "lastName": "Jones", "timezone": "Africa/Asmera", "dayEnds": 2
        }}})


    def test_root_user_is_protected(self):
        self.client.headers["Authorization"] = ""
        self.check_query_error(
            """{ user { firstName lastName } }""", message="Not authorized"
        )



class UserModificationTests(FunctionalTest):

    def test_can_update_email(self):
        result = self.client.execute("""mutation { updateEmail(
            email: "sarah@lytiko.com", password: "password"
        ) { email } }""")
        self.assertEqual(
            result["data"], {"updateEmail": {"email": "sarah@lytiko.com"}}
        )
        self.assertEqual(User.objects.get(id="1").email, "sarah@lytiko.com")
    

    def test_can_validate_updated_email(self):
        # Email must be unique
        self.check_query_error("""mutation { updateEmail(
            email: "guy@gmail.com", password: "password"
        ) { email } }""", message="already exists")

        # Email must be valid
        self.check_query_error("""mutation { updateEmail(
            email: "guy@gmail", password: "password"
        ) { email } }""", message="valid email")

        # Password must be correct
        self.check_query_error("""mutation { updateEmail(
            email: "sarah@lytiko.com", password: "password123"
        ) { email } }""", message="Password not correct")
    

    def test_can_update_password(self):
        result = self.client.execute("""mutation { updatePassword(
            current: "password", new: "warwick96"
        ) { success } }""")
        self.assertEqual(
            result["data"], {"updatePassword": {"success": True}}
        )
        self.assertTrue(User.objects.get(id="1").check_password("warwick96"))
    

    def test_can_validate_updated_password(self):
        # Password must be 9 or more characters
        self.check_query_error("""mutation { updatePassword(
            current: "password", new: "arwick96"
        ) { success } }""", message="too short")
        self.assertTrue(User.objects.get(id="1").check_password("password"))

        # Password can't be numeric
        self.check_query_error("""mutation { updatePassword(
            current: "password", new: "27589234759879230"
        ) { success } }""", message="numeric")
        self.assertTrue(User.objects.get(id="1").check_password("password"))

        # Password must be reasonably uncommon
        self.check_query_error("""mutation { updatePassword(
            current: "password", new: "password1"
        ) { success } }""", message="too common")
        self.assertTrue(User.objects.get(id="1").check_password("password"))

        # Password must be correct
        self.check_query_error("""mutation { updatePassword(
            current: "password123", new: "warwick96"
        ) { success } }""", message="password not correct")
        self.assertTrue(User.objects.get(id="1").check_password("password"))


    def test_can_update_basic_settings(self):
        result = self.client.execute("""mutation { updateBasicSettings(
            dayEnds: 5, timezone: ""
        ) { user { timezone dayEnds } } }""")
        self.assertEqual(
            result["data"], {"updateBasicSettings": {"user": {
                "timezone": "", "dayEnds": 5
            }}}
        )
        self.assertFalse(User.objects.get(id="1").timezone)
        self.assertEqual(User.objects.get(id="1").day_ends, 5)

        result = self.client.execute("""mutation { updateBasicSettings(
            dayEnds: 1, timezone: "GB-Eire"
        ) { user { timezone dayEnds } } }""")
        self.assertEqual(
            result["data"], {"updateBasicSettings": {"user": {
                "timezone": "GB-Eire", "dayEnds": 1
            }}}
        )
        self.assertEqual(str(User.objects.get(id="1").timezone), "GB-Eire")
        self.assertEqual(User.objects.get(id="1").day_ends, 1)
    

    def test_basic_settings_validation(self):
        # Day ends can't be less than 0
        self.check_query_error("""mutation { updateBasicSettings(
            dayEnds: -1, timezone: "GB-Eire"
        ) { user { timezone dayEnds } } }""", message="0 and 5")

        # Day ends can't be more than 5
        self.check_query_error("""mutation { updateBasicSettings(
            dayEnds: 6, timezone: "GB-Eire"
        ) { user { timezone dayEnds } } }""", message="0 and 5")

        # Timezone must be valid timezone
        self.check_query_error("""mutation { updateBasicSettings(
            dayEnds: 2, timezone: "Europe/Blackpool"
        ) { user { timezone dayEnds } } }""", message="Europe/Blackpool is not one of the available choices")



class UserAccountDeletionTests(FunctionalTest):

    def test_can_delete_user_account(self):
        result = self.client.execute("""mutation { deleteUser(
            password: "password"
        ) { success } }""")
        self.assertEqual(
            result["data"], {"deleteUser": {"success": True}}
        )
        self.assertTrue(User.objects.count(), 1)
        self.assertFalse(User.objects.filter(email="sarah@gmail.com"))


    def test_user_account_deletion_validation(self):
        # Password must be correct
        self.check_query_error("""mutation { deleteUser(
            password: "password123"
        ) { success } }""", message="Password not correct")
        self.assertTrue(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(email="sarah@gmail.com"))