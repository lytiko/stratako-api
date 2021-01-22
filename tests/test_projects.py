from .base import FunctionalTest, TokenFunctionaltest
from core.models import Project

class SlotQueryTests(TokenFunctionaltest):

    def test_get_projects(self):
        result = self.client.execute("""{ user {
            projects { name description color status }
        } }""")
        self.assertEqual(result["data"]["user"]["projects"], [
            {"name": "Get Rescued", "description": "Get everybody home", "status": 2, "color": "#0000ff"},
            {"name": "Neutralise Others", "description": "", "status": 1, "color": "#ff0000"},
        ])


    def test_get_project(self):
        result = self.client.execute("""{ user {
            project(id: 1) { name description color status }
        } }""")
        self.assertEqual(result["data"]["user"]["project"], {
            "name": "Get Rescued", "description": "Get everybody home", "status": 2, "color": "#0000ff"
        })


    def test_cant_get_invalid_project(self):
        self.check_query_error("""{ user {
            project(id: 10001) { name description color status }
        } }""", "Does not exist")
        self.check_query_error("""{ user {
            project(id: 1000) { name description color status }
        } }""", "Does not exist")
