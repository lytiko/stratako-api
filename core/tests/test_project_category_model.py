import time
from mixer.backend.django import mixer
from django.test import TestCase
from core.models import User, ProjectCategory

class ProjectCategoryCreationTests(TestCase):

    def test_can_create_project_category(self):
        category = ProjectCategory.objects.create(
            name="Category 1", user=mixer.blend(User), order=1
        )
        self.assertNotEqual(category.id, 1)
        self.assertEqual(category.order, 1)
        category.full_clean()
    

    def test_making_extra_categories_increases_order(self):
        user1, user2 = mixer.blend(User), mixer.blend(User)
        category = mixer.blend(ProjectCategory, user=user1, order=None)
        self.assertEqual(category.order, 1)
        category = mixer.blend(ProjectCategory, user=user1, order=None)
        self.assertEqual(category.order, 2)
        category = mixer.blend(ProjectCategory, user=user2, order=None)
        self.assertEqual(category.order, 1)
        category = mixer.blend(ProjectCategory, user=user1, order=None)
        self.assertEqual(category.order, 3)
        category = mixer.blend(ProjectCategory, user=user2, order=None)
        self.assertEqual(category.order, 2)
    

    def test_can_specify_category_order(self):
        category = mixer.blend(ProjectCategory, order=10)
        self.assertEqual(category.order, 10)
    

    def test_order_only_set_on_creation(self):
        user1 = mixer.blend(User)
        category = mixer.blend(ProjectCategory, user=user1, order=None)
        self.assertEqual(category.order, 1)
        mixer.blend(ProjectCategory, user=user1, order=None)
        mixer.blend(ProjectCategory, user=user1, order=None)
        category.name = "S"
        category.save()
        category.refresh_from_db()
        self.assertEqual(category.order, 1)



class ProjectCategoryOrderTests(TestCase):

    def test_category_ordered_by_order(self):
        user = mixer.blend(User)
        category1 = mixer.blend(ProjectCategory, user=user, order=1)
        category2 = mixer.blend(ProjectCategory, user=user, order=3)
        category3 = mixer.blend(ProjectCategory, user=user, order=2)
        self.assertEqual(list(ProjectCategory.objects.all()), [category1, category3, category2])




class ProjectCategoryMovingTests(TestCase):

    def test_can_move_to_current_position(self):
        user = mixer.blend(User)
        categorys = [
            mixer.blend(ProjectCategory, user=user, order=1),
            mixer.blend(ProjectCategory, user=user, order=2),
            mixer.blend(ProjectCategory, user=user, order=3),
            mixer.blend(ProjectCategory, user=user, order=4),
            mixer.blend(ProjectCategory, user=user, order=5),
        ]
        mixer.blend(ProjectCategory)
        categorys[2].move_to(2)
        categorys[2].refresh_from_db()
        self.assertEqual(categorys[2].order, 3)
    

    def test_can_move_to_right(self):
        user = mixer.blend(User)
        categorys = [
            mixer.blend(ProjectCategory, user=user, order=1),
            mixer.blend(ProjectCategory, user=user, order=2),
            mixer.blend(ProjectCategory, user=user, order=3),
            mixer.blend(ProjectCategory, user=user, order=4),
            mixer.blend(ProjectCategory, user=user, order=5),
        ]
        mixer.blend(ProjectCategory)
        with self.assertNumQueries(2):
            categorys[1].move_to(3)
        for category in categorys: category.refresh_from_db()
        self.assertEqual(categorys[0].order, 1)
        self.assertEqual(categorys[1].order, 4)
        self.assertEqual(categorys[2].order, 2)
        self.assertEqual(categorys[3].order, 3)
        self.assertEqual(categorys[4].order, 5)
    

    def test_can_move_to_left(self):
        user = mixer.blend(User)
        categorys = [
            mixer.blend(ProjectCategory, user=user, order=1),
            mixer.blend(ProjectCategory, user=user, order=2),
            mixer.blend(ProjectCategory, user=user, order=3),
            mixer.blend(ProjectCategory, user=user, order=4),
            mixer.blend(ProjectCategory, user=user, order=5),
        ]
        mixer.blend(ProjectCategory)
        with self.assertNumQueries(2):
            categorys[4].move_to(0)
        for category in categorys: category.refresh_from_db()
        self.assertEqual(categorys[0].order, 2)
        self.assertEqual(categorys[1].order, 3)
        self.assertEqual(categorys[2].order, 4)
        self.assertEqual(categorys[3].order, 5)
        self.assertEqual(categorys[4].order, 1)