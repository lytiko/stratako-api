import kirjava
import base64
import requests
import jwt
import json
import time
import os
from django.conf import settings
from django.contrib.auth.hashers import check_password
from .base import FunctionalTest, TokenFunctionaltest
from core.models import User

class SignupTests(FunctionalTest):

    def test_can_signup(self):
        users_at_start = User.objects.count()

        # Create user
        result = self.client.execute("""mutation { signup(
            email: "kate@gmail.com", password: "sw0rdfish123",
            name: "Kate Austen"
        ) { accessToken user { email name } } }""")

        # There's a new user
        self.assertEqual(result["data"]["signup"]["user"], {
            "email": "kate@gmail.com", "name": "Kate Austen"
        })
        self.assertEqual(User.objects.count(), users_at_start + 1)
        new_user = User.objects.last()
        self.assertEqual(new_user.email, "kate@gmail.com")
        self.assertEqual(new_user.name, "Kate Austen")
        self.assertNotEqual(new_user.password, "sw0rdfish123")
        self.assertLess(abs(time.time() - new_user.last_login), 3)
        self.assertLess(abs(time.time() - new_user.creation_time), 3)

        # An access token has been returned
        access_token = result["data"]["signup"]["accessToken"]
        algorithm, payload, secret = access_token.split(".")
        payload = json.loads(base64.b64decode(payload + "==="))
        self.assertEqual(payload["sub"], new_user.id)
        self.assertLess(time.time() - payload["iat"], 10)
        self.assertLess(time.time() - payload["expires"] - 900, 10)

        # A HTTP-only cookie has been set with the refresh token
        refresh_token = self.client.session.cookies["refresh_token"]
        algorithm, payload, secret = access_token.split(".")
        payload = json.loads(base64.b64decode(payload + "==="))
        self.assertEqual(payload["sub"], new_user.id)
        self.assertLess(time.time() - payload["iat"], 10)
        self.assertLess(time.time() - payload["expires"] - 31536000, 10)

        # The new user has two slots
        self.assertEqual(new_user.slots.count(), 2)
        self.assertEqual(new_user.slots.first().name, "Work")
        self.assertEqual(new_user.slots.last().name, "Personal")
    

    def test_signup_validation(self):
        users_at_start = User.objects.count()

        # Name must be short enough
        self.check_query_error("""mutation { signup(
            email: "kate@gmail.com", password: "sw0rdfish123",
            name: "000001111122222333334444455555666667777788888999990"
        ) { accessToken } }""", message="50 characters")
        self.assertEqual(User.objects.count(), users_at_start)

        # Email must be unique
        self.check_query_error("""mutation { signup(
            email: "jack@gmail.com", password: "sw0rdfish123",
            name: "Kate Austen"
        ) { accessToken } }""", message="already exists")
        self.assertEqual(User.objects.count(), users_at_start)
        self.assertFalse("refresh_token" in self.client.session.cookies)

        # Password must be 9 or more characters
        self.check_query_error("""mutation { signup(
            email: "kate@gmail.com", password: "sw0rd123",
            name: "Kate Austen"
        ) { accessToken } }""", message="too short")
        self.assertEqual(User.objects.count(), users_at_start)
        self.assertFalse("refresh_token" in self.client.session.cookies)

        # Password can't be numeric
        self.check_query_error("""mutation { signup(
            email: "kate@gmail.com", password: "238442378572385238",
            name: "Kate Austen"
        ) { accessToken } }""", message="numeric")
        self.assertEqual(User.objects.count(), users_at_start)
        self.assertFalse("refresh_token" in self.client.session.cookies)

        # Password must be reasonably uncommon
        self.check_query_error("""mutation { signup(
            email: "kate@gmail.com", password: "password123",
            name: "Kate Austen"
        ) { accessToken } }""", message="too common")
        self.assertEqual(User.objects.count(), users_at_start)
        self.assertFalse("refresh_token" in self.client.session.cookies)



class LoginTests(FunctionalTest):

    def test_can_login(self):
        # Send credentials
        result = self.client.execute("""mutation { login(
            email: "jack@gmail.com", password: "livetogetha",
        ) { accessToken user { email name } } }""")

        # User is returned
        self.assertEqual(result["data"]["login"]["user"], {
            "email": "jack@gmail.com", "name": "Jack Shephard"
        })

        # An access token has been returned
        access_token = result["data"]["login"]["accessToken"]
        algorithm, payload, secret = access_token.split(".")
        payload = json.loads(base64.b64decode(payload + "==="))
        self.assertEqual(payload["sub"], self.user.id)
        self.assertLess(time.time() - payload["iat"], 10)
        self.assertLess(time.time() - payload["expires"] - 900, 10)

        # A HTTP-only cookie has been set with the refresh token
        refresh_token = self.client.session.cookies["refresh_token"]
        algorithm, payload, secret = access_token.split(".")
        payload = json.loads(base64.b64decode(payload + "==="))
        self.assertEqual(payload["sub"], self.user.id)
        self.assertLess(time.time() - payload["iat"], 10)
        self.assertLess(time.time() - payload["expires"] - 31536000, 10)

        # Last login has been updated
        self.user.refresh_from_db()
        self.assertLess(time.time() - self.user.last_login, 10)
    

    def test_login_can_fail(self):
        # Incorrect email
        self.check_query_error("""mutation { login(
            email: "claire@gmail.com", password: "livetogetha"
        ) { accessToken} }""", message="Invalid credentials")
        self.assertFalse("refresh_token" in self.client.session.cookies)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.last_login)

        # Incorrect password
        self.check_query_error("""mutation { login(
            email: "jack@gmail.com", password: "wrongpassword"
        ) { accessToken} }""", message="Invalid credentials")
        self.assertFalse("refresh_token" in self.client.session.cookies)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.last_login)



class TokenRefreshTests(FunctionalTest):

    def test_can_refresh_token(self):
        # Send query with cookie
        original_refresh_token = self.user.make_refresh_jwt()
        cookie_obj = requests.cookies.create_cookie(
            domain="localhost.local", name="refresh_token",
            value=original_refresh_token
        )
        self.client.session.cookies.set_cookie(cookie_obj)
        result = self.client.execute("{ accessToken }")

        # An access token has been returned
        access_token = result["data"]["accessToken"]
        algorithm, payload, secret = access_token.split(".")
        payload = json.loads(base64.b64decode(payload + "==="))
        self.assertEqual(payload["sub"], self.user.id)
        self.assertLess(time.time() - payload["iat"], 10)
        self.assertLess(time.time() - payload["expires"] - 900, 10)

        # A new HTTP-only cookie has been set with the refresh token
        refresh_token = self.client.session.cookies["refresh_token"]
        algorithm, payload, secret = access_token.split(".")
        payload = json.loads(base64.b64decode(payload + "==="))
        self.assertEqual(payload["sub"], self.user.id)
        self.assertLess(time.time() - payload["iat"], 10)
        self.assertLess(time.time() - payload["expires"] - 31536000, 10)
    

    def test_token_refresh_can_fail(self):
        # No cookies
        self.check_query_error(
            "{ accessToken }", message="No refresh token"
        )
        self.assertFalse("refresh_token" in self.client.session.cookies)

        # Refresh token garbled
        cookie_obj = requests.cookies.create_cookie(
            domain="localhost.local", name="refresh_token", value="sadafasdf"
        )
        self.client.session.cookies.set_cookie(cookie_obj)
        self.check_query_error(
            "{ accessToken }", message="Refresh token not valid"
        )
        
        # Refresh token expired
        token = jwt.encode({
            "sub": self.user.id, "iat": 1000000000000, "expires": 2000
        }, settings.SECRET_KEY, algorithm="HS256").decode()
        cookie_obj = requests.cookies.create_cookie(
            domain="localhost.local", name="refresh_token", value=token
        )
        self.client.session.cookies.set_cookie(cookie_obj)
        self.check_query_error(
            "{ accessToken }", message="Refresh token not valid"
        )



class LogoutTests(TokenFunctionaltest):

    def test_can_logout(self):
        # No cookies to begin with
        self.assertFalse("refresh_token" in self.client.session.cookies)

        # Log in
        self.client.execute("""mutation { login(
            email: "jack@gmail.com", password: "livetogetha",
        ) { accessToken } }""")

        # Cookie set
        self.assertTrue("refresh_token" in self.client.session.cookies)

        # Log out
        result = self.client.execute("mutation { logout { success } }")

        # Cookie gone
        self.assertTrue(result["data"]["logout"]["success"])
        self.assertFalse("refresh_token" in self.client.session.cookies)
    

    def test_logout_works_without_cookie(self):
        # No cookies
        self.assertFalse("refresh_token" in self.client.session.cookies)

        # Log out
        result = self.client.execute("mutation { logout { success } }")

        # Still no cookie
        self.assertTrue(result["data"]["logout"]["success"])
        self.assertFalse("refresh_token" in self.client.session.cookies)



class UserQueryTests(TokenFunctionaltest):

    def test_can_get_user(self):
        # Get user
        result = self.client.execute("""{ user {
            email name lastLogin creationTime
        } }""")

        # Everything is correct
        self.assertEqual(result["data"]["user"], {
            "email": "jack@gmail.com",
            "name": "Jack Shephard", "lastLogin": None, "creationTime": 946684800,
        })
    

    def test_must_be_logged_in_to_get_user(self):
        del self.client.headers["Authorization"]
        self.check_query_error("""{ user {
            email name lastLogin
        } }""", message="Not authorized")



class PasswordUpdateTests(TokenFunctionaltest):

    def test_can_update_password(self):
        # Send new password
        result = self.client.execute("""mutation { updatePassword(
            current: "livetogetha", new: "warwick96"
        ) { success } }""")

        # Password is changed
        self.assertEqual(result["data"], {"updatePassword": {"success": True}})
        self.user.refresh_from_db()
        self.assertTrue(check_password("warwick96", self.user.password))
    

    def test_can_validate_updated_password(self):
        # Password must be 9 or more characters
        self.check_query_error("""mutation { updatePassword(
            current: "livetogetha", new: "arwick96"
        ) { success } }""", message="too short")
        self.user.refresh_from_db()
        self.assertFalse(check_password("arwick96", self.user.password))
        self.assertTrue(check_password("livetogetha", self.user.password))

        # Password can't be numeric
        self.check_query_error("""mutation { updatePassword(
            current: "livetogetha", new: "27589234759879230"
        ) { success } }""", message="numeric")
        self.user.refresh_from_db()
        self.assertFalse(check_password("27589234759879230", self.user.password))
        self.assertTrue(check_password("livetogetha", self.user.password))

        # Password must be reasonably uncommon
        self.check_query_error("""mutation { updatePassword(
            current: "livetogetha", new: "password1"
        ) { success } }""", message="too common")
        self.user.refresh_from_db()
        self.assertFalse(check_password("password1", self.user.password))
        self.assertTrue(check_password("livetogetha", self.user.password))

        # Password must be correct
        self.check_query_error("""mutation { updatePassword(
            current: "livetogetha123", new: "warwick96"
        ) { success } }""", message="password not correct")
        self.user.refresh_from_db()
        self.assertFalse(check_password("warwick96", self.user.password))
        self.assertTrue(check_password("livetogetha", self.user.password))

        # Token must be given
        del self.client.headers["Authorization"]
        self.check_query_error("""mutation { updatePassword(
            current: "livetogetha", new: "warwick96"
        ) { success } }""", message="Not authorized")



class UserModificationTests(TokenFunctionaltest):

    def test_can_update_user_info(self):
        # Update info
        result = self.client.execute("""mutation { updateUser(
            email: "jack@island.com", name: "Dr Jack"
        ) { user { email name } } }""")

        # The new user info is returned
        self.assertEqual(result["data"]["updateUser"]["user"], {
            "email": "jack@island.com", "name": "Dr Jack",
        })

        # The user has updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "jack@island.com")
        self.assertEqual(self.user.name, "Dr Jack")
    

    def test_cant_edit_user_when_not_logged_in(self):
        del self.client.headers["Authorization"]
        self.check_query_error("""mutation { updateUser(
            email: "jack@island.com", name: "Dr Jack"
        ) { user { email name } } }""", message="Not authorized")



class UserDeletionTests(TokenFunctionaltest):

    def test_can_delete_account(self):
        # Send deletion mutation
        users_at_start = User.objects.count()
        result = self.client.execute("""mutation { deleteUser { success } }""")

        # It works
        self.assertTrue(result["data"]["deleteUser"]["success"])
        self.assertEqual(User.objects.count(), users_at_start - 1)
        self.assertFalse(User.objects.filter(email="jack@gmail.com").count())
    

    def test_account_deletion_can_fail(self):
        users_at_start = User.objects.count()

        # Invalid token
        self.client.headers["Authorization"] = "Bearer qwerty"
        self.check_query_error(
            """mutation { deleteUser { success } }""",
            message="Invalid or missing token"
        )
        self.assertEqual(User.objects.count(), users_at_start)

        # No token
        del self.client.headers["Authorization"]
        self.check_query_error(
            """mutation { deleteUser { success } }""",
            message="Invalid or missing token"
        )
        self.assertEqual(User.objects.count(), users_at_start)