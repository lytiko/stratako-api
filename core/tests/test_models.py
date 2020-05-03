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
    

    def test_can_move_goals_within_category(self):
        
        category = mixer.blend(GoalCategory)
        g1 = mixer.blend(Goal, order=0, category=category)
        g2 = mixer.blend(Goal, order=1, category=category)
        g3 = mixer.blend(Goal, order=2, category=category)
        g4 = mixer.blend(Goal, order=3, category=category)
        g5 = mixer.blend(Goal, order=4, category=category)
        g6 = mixer.blend(Goal, order=5, category=category)
        g7 = mixer.blend(Goal, order=3)
        with self.assertNumQueries(2):
            g4.move(2)
        goals = list(category.goals.all())
        self.assertEqual(goals[0].id, g1.id)
        self.assertEqual(goals[1].id, g2.id)
        self.assertEqual(goals[2].id, g4.id)
        self.assertEqual(goals[3].id, g3.id)
        self.assertEqual(goals[4].id, g5.id)
        self.assertEqual(goals[5].id, g6.id)
        g7.refresh_from_db()
        self.assertEqual(g7.order, 3)
        self.assertEqual([g.order for g in goals], [0, 1, 2, 3, 4, 5])
    

    def test_can_move_goals_between_categories(self):
        user = mixer.blend(User)
        category1 = mixer.blend(GoalCategory, user=user)
        category2 = mixer.blend(GoalCategory, user=user)
        g1 = mixer.blend(Goal, order=0, category=category1)
        g2 = mixer.blend(Goal, order=1, category=category1)
        g3 = mixer.blend(Goal, order=2, category=category1)
        g4 = mixer.blend(Goal, order=0, category=category2)
        g5 = mixer.blend(Goal, order=1, category=category2)
        g6 = mixer.blend(Goal, order=2, category=category2)
        g7 = mixer.blend(Goal, order=3)
        with self.assertNumQueries(6):
            g2.move(0, category2.id)
        goals1 = list(category1.goals.all())
        self.assertEqual(len(goals1), 2)
        self.assertEqual(goals1[0].id, g1.id)
        self.assertEqual(goals1[1].id, g3.id)
        goals2 = list(category2.goals.all())
        self.assertEqual(len(goals2), 4)
        self.assertEqual(goals2[0].id, g2.id)
        self.assertEqual(goals2[1].id, g4.id)
        self.assertEqual(goals2[2].id, g5.id)
        self.assertEqual(goals2[3].id, g6.id)
        g7.refresh_from_db()
        self.assertEqual(g7.order, 3)
    

    def test_cannot_move_goal_to_other_users_category(self):
        category1 = mixer.blend(GoalCategory)
        category2 = mixer.blend(GoalCategory)
        g1 = mixer.blend(Goal, order=0, category=category1)
        g2 = mixer.blend(Goal, order=1, category=category1)
        g3 = mixer.blend(Goal, order=2, category=category1)
        g4 = mixer.blend(Goal, order=0, category=category2)
        g5 = mixer.blend(Goal, order=1, category=category2)
        g6 = mixer.blend(Goal, order=2, category=category2)
        with self.assertRaises(GoalCategory.DoesNotExist):
            g2.move(0, category2.id)
