import pytz
from unittest.mock import patch, Mock
from mixer.backend.django import mixer
from django.test import TestCase
from core.forms import *

class UserFormTests(TestCase):

    def test_can_create_user(self):
        form = UserForm({
         "email": "john", "timezone": "UTC",
         "email": "a@b.co", "password": "12345678"
        })
        self.assertTrue(form.is_valid())
    

    def test_can_update_user(self):
        user = mixer.blend(User)
        password = user.password
        form = UserForm(instance=user, data={"email": "sally@x.com"})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(form.instance.email, "sally@x.com")
        self.assertEqual(form.instance.password, password)
        form = UserForm(instance=user, data={"email": "b@c.co", "password": "abcabcabc"})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(form.instance.email, "b@c.co")
        self.assertNotEqual(form.instance.password, password)
        self.assertNotEqual(form.instance.password, "abcabcabc")


    def test_user_form_validates_password(self):
        form = UserForm({
         "email": "john", "timezone": "UTC",
         "email": "a@b.co", "password": "1234567"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("8 characters", form.errors["password"][0])
        form = UserForm({
         "email": "a@b.co", "password": "12345678"
        })
        self.assertTrue(form.is_valid())



class LoginFormTests(TestCase):

    def test_login_form_can_reject(self):
        form = LoginForm({"email": "john@g.com", "password": "123456789"})
        self.assertFalse(form.validate_credentials())


    def test_login_form_can_login(self):
        john = mixer.blend(User, email="john@g.com")
        john.set_password("12345678")
        john.save()
        form = LoginForm({"email": "john@g.com", "password": "12345678"})
        self.assertEqual(form.validate_credentials(), john)