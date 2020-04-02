import os
from contextlib import redirect_stderr
import kirjava
from datetime import datetime
from freezegun import freeze_time
from django.test.utils import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from core.models import User

class FunctionalTest(StaticLiveServerTestCase):

    fixtures = [
        "users.json"
    ]

    def setUp(self):
        self.freezer = freeze_time("2000-01-14 15:00:00") #UTC time
        self.freezer.start()
        self.user = User.objects.get(email="sarah@gmail.com")
        self.user.set_password("password")
        self.user.save()
        self.client = kirjava.Client(self.live_server_url)
        self.client.headers["Accept"] = "application/json"
        self.client.headers["Content-Type"] = "application/json"
        self.client.headers["Authorization"] = self.user.create_jwt()
    

    def tearDown(self):
        self.freezer.stop()
    

    def check_query_error(self, query, message="does not exist"):
        """Sends a query and asserts that the server report the object doesn't
        exist."""

        with open(os.devnull, "w") as fnull:
            with redirect_stderr(fnull) as err:
                result = self.client.execute(query)
                self.assertIn(message, result["errors"][0]["message"])