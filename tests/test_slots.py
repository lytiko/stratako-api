import kirjava
import base64
import requests
import jwt
import json
import time
import os
from django.conf import settings
from django.contrib.auth.hashers import check_password
from .base import FunctionalTest, TokenFunctionaltest
from core.models import User

class SlotQueryTests(TokenFunctionaltest):

    def test_get_slots(self):
        result = self.client.execute("""{ user {
            slots { name order }
        } }""")
        self.assertEqual(result["data"]["user"]["slots"], [
            {"name": "Public Work", "order": 1},
            {"name": "Private Work", "order": 2},
        ])