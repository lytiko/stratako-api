from mixer.backend.django import mixer
from django.test import TestCase
from core.models import *

class TaskCreationTests(TestCase):

    def test_tasks_auto_add_order_if_not_given(self):
        operation1 = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        operation2 = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        task = mixer.blend(Task, operation=operation1, order=None)
        self.assertEqual(task.order, 1)
        task = mixer.blend(Task, operation=operation1, order=None)
        self.assertEqual(task.order, 2)
        task = mixer.blend(Task, operation=operation2, order=None)
        self.assertEqual(task.order, 1)
        task = mixer.blend(Task, operation=operation1, order=None)
        self.assertEqual(task.order, 3)
    

    def test_tasks_can_take_custom_order(self):
        operation = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        task = mixer.blend(Task, operation=operation, order=10)
        self.assertEqual(task.order, 10)
    

    def test_tasks_can_have_order_changed(self):
        operation = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        task = mixer.blend(Task, operation=operation, order=None)
        self.assertEqual(task.order, 1)
        task.order = 10
        task.save()
        self.assertEqual(task.order, 10)
        task.name = "XYZ"
        task.save()
        self.assertEqual(task.order, 10)

