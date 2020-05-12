from unittest.mock import patch, Mock, PropertyMock, MagicMock
from mixer.backend.django import mixer
from django.test import TestCase
from django.conf import settings
from core.middleware import *

class ApiAuthMiddlewareTests(TestCase):

    def setUp(self):
        self.request = Mock(path="/")
        self.callback = MagicMock()
        self.mw = AuthenticationMiddleware(self.callback)
        self.user = mixer.blend(User, username="john")


    def test_middleware_rejects_requests_without_token(self):
        response = self.mw(self.request)
        self.assertIsNone(self.request.user)


    def test_middleware_rejects_incorrect_token(self):
        self.request.META = {"HTTP_AUTHORIZATION": "12345"}
        response = self.mw(self.request)
        self.assertIsNone(self.request.user)
    

    def test_middleware_rejects_expired_token(self):
        token = jwt.encode({
            "sub": self.user.id, "name": "john", "iat": int(time.time()) - 86400 * 15
        }, settings.SECRET_KEY, algorithm="HS256").decode()
        self.request.META = {"HTTP_AUTHORIZATION": token}
        response = self.mw(self.request)
        self.assertIsNone(self.request.user)
    

    def test_middleware_rejects_unknown_user(self):
        token = jwt.encode({
            "sub": 99, "name": "john", "iat": int(time.time())
        }, settings.SECRET_KEY, algorithm="HS256").decode()
        self.request.META = {"HTTP_AUTHORIZATION": token}
        response = self.mw(self.request)
        self.assertIsNone(self.request.user)


    def test_middleware_lets_correct_tokens_through(self):
        token = jwt.encode({
            "sub": self.user.id, "name": "john", "iat": int(time.time())
        }, settings.SECRET_KEY, algorithm="HS256").decode()
        self.request.META = {"HTTP_AUTHORIZATION": token}
        response = self.mw(self.request)
        self.assertIs(response, self.callback.return_value)
        self.assertEqual(self.request.user, self.user)