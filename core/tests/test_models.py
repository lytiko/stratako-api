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
    

    def test_user_goals(self):
        user = mixer.blend(User)
        c1, c2 = mixer.blend(GoalCategory, user=user), mixer.blend(GoalCategory)
        g1 = mixer.blend(Goal, category=c1, value=10)
        g2 = mixer.blend(Goal, category=c1, value=15)
        g3 = mixer.blend(Goal, category=c2)
        g4 = mixer.blend(Goal, category=c2)
        self.assertEqual(set(user.goals.all()), {g1, g2})



class GoalCategoryTests(TestCase):

    def test_can_make_new_goal_category(self):
        kwargs = {
            "name": "Name", "description": "DDD",
            "user": mixer.blend(User), "order": 1
        }
        category = GoalCategory.objects.create(**kwargs)
        for arg in ["description"]:
            args = {k: v for k, v in kwargs.items() if k != arg}
            GoalCategory.objects.create(**args)



class GoalTests(TestCase):

    def test_can_make_new_goal(self):
        kwargs = {
            "name": "Name", "description": "DDD",
            "category": mixer.blend(GoalCategory), "order": 1
        }
        goal = Goal.objects.create(**kwargs)
        for arg in ["description"]:
            args = {k: v for k, v in kwargs.items() if k != arg}
            Goal.objects.create(**args)
