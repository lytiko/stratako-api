from unittest.mock import patch, Mock, PropertyMock, MagicMock
from django.test import TestCase
from core.views import *

class SignupViewTests(TestCase):

    def test_get_is_405(self):
        request = Mock(method="GET")
        response = signup(request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'{"error": "Method not allowed"}')
    

    @patch("core.views.UserForm")
    def test_invalid_form_is_422(self, mock_form):
        request = Mock(method="POST", body=b'{"a": 1}')
        mock_form.return_value.is_valid.return_value = False
        mock_form.return_value.errors = {"E": "EE"}
        response = signup(request)
        mock_form.assert_called_with({"a": 1})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.content, b'{"error": {"E": "EE"}}')
    

    @patch("core.views.UserForm")
    def test_invalid_form_is_422(self, mock_form):
        request = Mock(method="POST", body=b'{"a": 1}')
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.save.return_value.create_jwt.return_value = "token"
        response = signup(request)
        mock_form.assert_called_with({"a": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"message": "token"}')



class LoginViewTests(TestCase):

    def test_get_is_405(self):
        request = Mock(method="GET")
        response = login(request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'{"error": "Method not allowed"}')
    

    @patch("core.views.LoginForm")
    def test_can_handle_wrong_credentials(self, mock_form):
        request = Mock(method="POST", body=b'{"a": 1}')
        mock_form.return_value.validate_credentials.return_value = False
        mock_form.return_value.errors = {"E": "EE"}
        response = login(request)
        mock_form.assert_called_with({"a": 1})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.content, b'{"error": {"E": "EE"}}')
    

    @patch("core.views.LoginForm")
    def test_can_login(self, mock_form):
        request = Mock(method="POST", body=b'{"a": 1}')
        mock_form.return_value.validate_credentials.return_value.create_jwt.return_value = "token"
        response = login(request)
        mock_form.assert_called_with({"a": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"message": "token"}')