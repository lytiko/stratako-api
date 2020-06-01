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



class LoginFormTests(TestCase):

    def test_login_form_can_reject(self):
        form = LoginForm({"email": "john@john.com", "password": "123456789"})
        self.assertFalse(form.validate_credentials())
        self.assertIn("Invalid credentials", form.errors["email"][0])


    def test_login_form_can_login(self):
        john = mixer.blend(User, email="john@gmail.com")
        john.set_password("12345678")
        john.save()
        form = LoginForm({"email": "john@gmail.com", "password": "12345678"})
        self.assertEqual(form.validate_credentials(), john)



class UpdateEmailFormTests(TestCase):

    def test_form_can_update_email(self):
        john = mixer.blend(User, email="john@gmail.com")
        john.set_password("password")
        form = UpdateEmailForm({"email": "new@email.com", "password": "password"}, instance=john)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(john.email, "new@email.com")
    

    def test_form_can_reject_email(self):
        john = mixer.blend(User, email="john@gmail.com")
        john.set_password("password")
        mixer.blend(User, email="sam@gmail.com")
        form = UpdateEmailForm({"email": "sam@gmail.com", "password": "password"}, instance=john)
        self.assertIn("already exists", form.errors["email"][0])
        self.assertFalse(form.is_valid())
        form = UpdateEmailForm({"email": "sam@gmail", "password": "password"}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("valid email", form.errors["email"][0])
    

    def test_form_can_reject_password(self):
        john = mixer.blend(User, email="john@gmail.com")
        john.set_password("password")
        form = UpdateEmailForm({"email": "new@email.com", "password": "password123"}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("Password not correct", form.errors["password"][0])



class UpdatePasswordFormTests(TestCase):

    def test_form_can_update_password(self):
        john = mixer.blend(User, email="john@gmail.com")
        john.set_password("password")
        form = UpdatePasswordForm({"current": "password", "new": "warwick96"}, instance=john)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(john.check_password("warwick96"))
    

    def test_form_can_reject_current_password(self):
        john = mixer.blend(User, email="john@gmail.com")
        john.set_password("password")
        form = UpdatePasswordForm({"current": "xxxxxxxxx", "new": "warwick96"}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("password not correct", form.errors["current"][0])
    

    def test_form_can_reject_new_password(self):
        john = mixer.blend(User, email="john@gmail.com")
        john.set_password("password")
        form = UpdatePasswordForm({"current": "password", "new": "arwick96"}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("9 characters", form.errors["new"][0])
        form = UpdatePasswordForm({"current": "password", "new": "3738426578326"}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("numeric", form.errors["new"][0])
        form = UpdatePasswordForm({"current": "password", "new": "password1"}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("too common", form.errors["new"][0])



class UpdateBasicSettingsFormTests(TestCase):

    def test_form_can_update_basic_settings(self):
        john = mixer.blend(User, email="john@gmail.com")
        form = UpdateBasicSettingsForm({"day_ends": 4, "timezone": ""}, instance=john)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(john.day_ends, 4)
        self.assertEqual(john.timezone, "")
    

    def test_form_can_reject_day_ends(self):
        john = mixer.blend(User, email="john@gmail.com")
        form = UpdateBasicSettingsForm({"day_ends": -1, "timezone": ""}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("between 0 and 5", form.errors["day_ends"][0])
        form = UpdateBasicSettingsForm({"day_ends": 6, "timezone": ""}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("between 0 and 5", form.errors["day_ends"][0])
    

    def test_form_can_reject_timezone(self):
        john = mixer.blend(User, email="john@gmail.com")
        form = UpdateBasicSettingsForm({"day_ends": 5, "timezone": "Europe/Bacup"}, instance=john)
        self.assertFalse(form.is_valid())
        self.assertIn("valid choice", form.errors["timezone"][0])