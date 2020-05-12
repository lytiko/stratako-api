from mixer.backend.django import mixer
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import *

class UserCreationTests(TestCase):

    def test_can_create_user(self):
        kwargs = {"email": "chris@uni.edu", "first_name": "C", "last_name": "J"}
        user = User.objects.create(**kwargs)
        self.assertNotEqual(user.id, 1)
        for arg in ["email", "first_name", "last_name"]:

            kwargs["email"] += "x"
            args = {k: v for k, v in kwargs.items() if k != arg}
            with self.assertRaises(ValidationError):
                User.objects.create(**args).full_clean()


    def test_user_passwords_handled(self):
        user = mixer.blend(User)
        user.set_password("12345678")
        user.save()
        self.assertNotEqual(user.password, "12345678")



class UserJwtTests(TestCase):

    def test_jwt_creation(self):
        user = mixer.blend(User)
        token = user.create_jwt()
        token = jwt.decode(token, settings.SECRET_KEY)
        self.assertEqual(token["sub"], user.id)
        self.assertLessEqual(time.time() - token["iat"], 2)