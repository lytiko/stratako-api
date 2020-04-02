import requests
import jwt
import os
from contextlib import redirect_stderr
from django.conf import settings
from core.models import User
from .base import FunctionalTest

class SignupTests(FunctionalTest):

    def test_can_signup(self):
        # Send response
        response = requests.post(self.live_server_url + "/signup/", json={
         "email": "will@gmail.com", "password": "12345678",
        }, headers={"Content-type": "application/json"})

        # There is a new user
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(email="will@gmail.com").email, "will@gmail.com")
        self.assertNotEqual(User.objects.get(email="will@gmail.com").password, "12345678")

        # The token sent back makes sense
        token = response.json()["message"]
        decoded_token = jwt.decode(token, settings.SECRET_KEY)
        self.assertEqual(decoded_token["name"], "will@gmail.com")
    

    def test_signup_validation(self):
        # Can't omit values
        response = requests.post(self.live_server_url + "/signup/", json={
         "password": "12345678"
        }, headers={"Content-type": "application/json"})
        self.assertEqual(response.json()["error"]["email"], ["This field is required."])

        # Email must be unique
        response = requests.post(self.live_server_url + "/signup/", json={
         "email": "sarah@gmail.com", "password": "12345678",
        }, headers={"Content-type": "application/json"})
        self.assertEqual(response.json()["error"]["email"], ["User with this Email already exists."])

        # Password must be long enough
        response = requests.post(self.live_server_url + "/signup/", json={
         "email": "will@gmail.com", "password": "1234567",
        }, headers={"Content-type": "application/json"})
        self.assertEqual(response.json()["error"]["password"], ["Password must be at least 8 characters."])



class LoginTests(FunctionalTest):

    def test_can_log_in(self):
        # Send response
        response = requests.post(self.live_server_url + "/login/", json={
         "email": "sarah@gmail.com", "password": "password"
        }, headers={"Content-type": "application/json"})

        # The token sent back makes sense
        token = response.json()["message"]
        decoded_token = jwt.decode(token, settings.SECRET_KEY)
        self.assertEqual(decoded_token["name"], "sarah@gmail.com")


    def test_can_reject_invalid_credentials(self):
        # Send response
        response = requests.post(self.live_server_url + "/login/", json={
         "email": "sarah@gmail.com", "password": "password!"
        }, headers={"Content-type": "application/json"})

        # Didn't work
        self.assertEqual(response.json()["error"]["email"], ["Invalid credentials."])



class GraphqlProtectionTests(FunctionalTest):
    
    def test_cant_use_api_without_token(self):
        del self.client.headers["Authorization"]
        result = self.client.execute("{user {username email timezone }}")
        self.assertEqual(result, {"error": "Unauthorized"})


    def test_cant_use_api_without_valid_token(self):
        self.client.headers["Authorization"] = "1321435.34532454.23454325"
        result = self.client.execute("{user {username email timezone }}")
        self.assertEqual(result, {"error": "Unauthorized"})


    def test_cant_use_api_without_recent_token(self):
        token = User.objects.get(email="sarah@gmail.com").create_jwt()
        token = jwt.decode(token, settings.SECRET_KEY)
        token["iat"] -= ((15 * 24 * 60 * 60) + 1)
        self.client.headers["Authorization"] = jwt.encode(token, settings.SECRET_KEY)
        result = self.client.execute("{user {email}}")
        self.assertEqual(result, {"error": "Unauthorized"})