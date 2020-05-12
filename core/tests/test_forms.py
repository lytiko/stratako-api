import pytz
from unittest.mock import patch, Mock
from mixer.backend.django import mixer
from django.test import TestCase
from django.test import override_settings
from core.forms import *

class SignupFormTests(TestCase):

    @override_settings(EMAILS=["a@b.co"])
    def test_can_create_user(self):
        form = SignupForm({
         "first_name": "john", "last_name": "Parry",
         "email": "a@b.co", "password": "michaelmas"
        })
        self.assertTrue(form.is_valid())
    

    @override_settings(EMAILS=["a@b.co"])
    def test_user_form_validates_password(self):
        form = SignupForm({
            "first_name": "john", "last_name": "Parry",
            "email": "a@b.co", "password": "michael"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("9 characters", form.errors["password"][0])
        form = SignupForm({
            "first_name": "john", "last_name": "Parry",
            "email": "a@b.co", "password": "3782567823567856783926"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("numeric", form.errors["password"][0])
        form = SignupForm({
            "first_name": "john", "last_name": "Parry",
            "email": "a@b.co", "password": "password123"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("common", form.errors["password"][0])
        form = SignupForm({
            "first_name": "john", "last_name": "Parry",
            "email": "a@b.co", "password": "michaelmas"
        })
        self.assertTrue(form.is_valid())



class LoginFormTests(TestCase):

    def test_login_form_can_reject(self):
        form = LoginForm({"email": "john@john.com", "password": "123456789"})
        self.assertFalse(form.validate_credentials())


    def test_login_form_can_login(self):
        john = mixer.blend(User, email="john@gmail.com")
        john.set_password("12345678")
        john.save()
        form = LoginForm({"email": "john@gmail.com", "password": "12345678"})
        self.assertEqual(form.validate_credentials(), john)