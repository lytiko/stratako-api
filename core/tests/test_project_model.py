import time
from mixer.backend.django import mixer
from django.test import TestCase
from core.models import User, Project

class ProjectCreationTests(TestCase):

    def test_can_create_project(self):
        project = Project.objects.create(
            name="Slot 1", description="D", color="black", user=mixer.blend(User)
        )
        self.assertNotEqual(project.id, 1)
        self.assertLess(abs(project.creation_time), time.time())
        project.full_clean()



class ProjectOrderingTests(TestCase):

    def test_projects_ordered_by_creation_time(self):
        user = mixer.blend(User)
        project1 = mixer.blend(Project, user=user, creation_time=1)
        project2 = mixer.blend(Project, user=user, creation_time=3)
        project3 = mixer.blend(Project, user=user, creation_time=2)
        self.assertEqual(list(Project.objects.all()), [project1, project3, project2])