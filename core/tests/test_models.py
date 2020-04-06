import time
from mixer.backend.django import mixer
from django.test import TestCase
from django.db.utils import IntegrityError
from core.models import *

class UserTests(TestCase):

    def test_can_make_new_user(self):
        user = User.objects.create(email="john@mail.com")
        user.set_password("12345678")
        user.save()
        self.assertNotEqual(user.password, "12345678")
    

    def test_email_must_be_unique(self):
        mixer.blend(User, email="user@mail.com")
        with self.assertRaises(IntegrityError):
            User.objects.create(email="user@mail.com")
    

    def test_user_tokens(self):
        user = User.objects.create(email="john@mail.com")
        token = user.create_jwt()
        token = jwt.decode(token, settings.SECRET_KEY)
        self.assertEqual(token["sub"], user.id)
        self.assertEqual(token["name"], user.email)
        self.assertLessEqual(time.time() - token["iat"], 2)



class GoalTests(TestCase):

    def test_can_make_new_goal(self):
        kwargs = {
            "name": "Name", "description": "DDD",
            "user": mixer.blend(User), "order": 1
        }
        goal = Goal.objects.create(**kwargs)
        for arg in ["description"]:
            args = {k: v for k, v in kwargs.items() if k != arg}
            Goal.objects.create(**args)
