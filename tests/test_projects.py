from .base import FunctionalTest, TokenFunctionaltest
from core.models import Project

class ProjectQueryTests(TokenFunctionaltest):

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



class ProjectMutationTests(TokenFunctionaltest):

    def test_can_create_project(self):
        result = self.client.execute("""mutation { createProject(
            name: "Project 3" description: "3rd project" status: 4 color: "#00ff00"
        ) { project { name description color status } } }""")
        self.assertEqual(result["data"]["createProject"]["project"], {
            "name": "Project 3", "description": "3rd project", "status": 4, "color": "#00ff00"
        })
    

    def test_project_creation_validation(self):
        projects_at_start = Project.objects.count()

        # Name must be short enough
        self.check_query_error("""mutation { createProject(
            name: "0000000000111111111122222222223333333333444444444455555555556666666666777777777788888888889999999999a"
            description: "3rd project" status: 4 color: "#00ff00"
        ) { project { name description color status } } }""", message="100 characters")
        self.assertEqual(Project.objects.count(), projects_at_start)

        # Status must be valid
        self.check_query_error("""mutation { createProject(
            name: "Project 3"
            description: "3rd project" status: 0 color: "#00ff00"
        ) { project { name description color status } } }""", message="valid")
        self.assertEqual(Project.objects.count(), projects_at_start)
        self.check_query_error("""mutation { createProject(
            name: "Project 3"
            description: "3rd project" status: 7 color: "#00ff00"
        ) { project { name description color status } } }""", message="valid")
        self.assertEqual(Project.objects.count(), projects_at_start)
    

    def test_project_creation_protection(self):
        del self.client.headers["Authorization"]
        self.check_query_error("""mutation { createProject(
            name: "Project 3" description: "3rd project" status: 4 color: "#00ff00"
        ) { project { name description color status } } }""", message="Not authorized")
    

    def test_can_edit_project(self):
        result = self.client.execute("""mutation { updateProject(
            id: 1, name: "Project 3" description: "3rd project" status: 4 color: "#00ff00"
        ) { project { name description color status } } }""")
        self.assertEqual(result["data"]["updateProject"]["project"], {
            "name": "Project 3", "description": "3rd project", "status": 4, "color": "#00ff00"
        })
    

    def test_project_editing_validation(self):
        # Project must exist
        self.check_query_error("""mutation { updateProject(
            id: 99, name: "Project 3" description: "3rd project" status: 4 color: "#00ff00"
        ) { project { name description color status } } }""", message="Does not exist")

        # project must be user's
        self.check_query_error("""mutation { updateProject(
            id: 3, name: "Project 3" description: "3rd project" status: 4 color: "#00ff00"
        ) { project { name description color status } } }""", message="Does not exist")
    

    def test_project_editing_protection(self):
        del self.client.headers["Authorization"]
        self.check_query_error("""mutation { updateProject(
            id: 1, name: "Project 3" description: "3rd project" status: 4 color: "#00ff00"
        ) { project { name description color status } } }""", message="Not authorized")
    

    def test_can_delete_project(self):
        # Send deletion mutation
        projects_at_start = Project.objects.count()
        result = self.client.execute("""mutation { deleteProject(id: 1) { success } }""")

        # It works
        self.assertTrue(result["data"]["deleteProject"]["success"])
        self.assertEqual(Project.objects.count(), projects_at_start - 1)
        self.assertFalse(Project.objects.filter(name="Get Rescued").count())
    

    def test_cant_delete_invalid_project(self):
        # Doesn't exist
        self.check_query_error("""mutation { deleteProject(id: 5) {
            success
        } }""", message="Does not exist")

        # Other user's
        self.check_query_error("""mutation { deleteProject(id: 3) {
            success
        } }""", message="Does not exist")
    

    def test_project_deletion_protection(self):
        del self.client.headers["Authorization"]
        self.check_query_error(
            """mutation { deleteProject(id: 1) { success } }""", message="Not authorized"
        )