import time
from mixer.backend.django import mixer
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import *

class TaskCreationTests(TestCase):

    def test_tasks_auto_add_order_if_not_given(self):
        # Operation
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

        # Project
        project = mixer.blend(Project)
        task = mixer.blend(Task, project=project, order=None)
        self.assertEqual(task.order, 1)
        task = mixer.blend(Task, project=project, order=None)
        self.assertEqual(task.order, 2)
    

    def test_tasks_can_take_custom_order(self):
        # Operation
        operation = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        task = mixer.blend(Task, operation=operation, order=10)
        self.assertEqual(task.order, 10)

        # Project
        project = mixer.blend(Project)
        task = mixer.blend(Task, project=project, order=10)
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
    

    def test_operation_or_project(self):
        operation = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        project = mixer.blend(Project)
        with self.assertRaises(ValidationError):
            Task.objects.create().full_clean()
        with self.assertRaises(ValidationError):
            Task.objects.create(name="T", operation=operation, project=project).full_clean()
        Task.objects.create(name="T", operation=operation).full_clean()
        Task.objects.create(name="T", project=project).full_clean()



class TaskOrderTests(TestCase):

    def test_tasks_ordered_by_order(self):
        operation = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        task5 = mixer.blend(Task, operation=operation, order=5)
        task1 = mixer.blend(Task, operation=operation, order=1)
        task4 = mixer.blend(Task, operation=operation, order=4)
        task3 = mixer.blend(Task, operation=operation, order=3)
        task2 = mixer.blend(Task, operation=operation, order=2)
        self.assertEqual(list(Task.objects.all()), [task1, task2, task3, task4, task5])



class TaskTogglingTests(TestCase):

    def test_can_toggle_task(self):
        operation = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        task = mixer.blend(Task, operation=operation)
        self.assertIsNone(task.completed)
        task.toggle()
        self.assertLess(time.time() - task.completed, 2)
        task.toggle()
        self.assertIsNone(task.completed)

        

class TaskMovingTests(TestCase):

    def setUp(self):
        self.operation = mixer.blend(Operation, slot=mixer.blend(Slot, operation=None))
        self.project = mixer.blend(Project)
        self.tasks = [mixer.blend(Task, operation=self.operation, order=o) for o in range(1, 6)]
        self.project_tasks = [mixer.blend(Task, project=self.project, order=o) for o in range(1, 6)]


    def test_can_stay_in_place(self):
        # Operations
        self.tasks[0].move(0)
        for order, task in enumerate(self.tasks, start=1):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
        
        # Projects
        self.project_tasks[0].move(0)
        for order, task in enumerate(self.project_tasks, start=1):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
    

    def test_can_move_down_operation(self):
        # Operations
        with self.assertNumQueries(2):
            self.tasks[0].move(1)
        for order, task in zip([2, 1, 3, 4, 5], self.tasks):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
        self.tasks[2].move(4)
        for order, task in zip([2, 1, 5, 3, 4], self.tasks):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
        
        # Projects
        with self.assertNumQueries(2):
            self.project_tasks[0].move(1)
        for order, task in zip([2, 1, 3, 4, 5], self.project_tasks):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
        self.project_tasks[2].move(4)
        for order, task in zip([2, 1, 5, 3, 4], self.project_tasks):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
    

    def test_can_move_up_operation(self):
        # Operations
        self.tasks[4].move(3)
        for order, task in zip([1, 2, 3, 5, 4], self.tasks):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
        self.tasks[1].move(0)
        for order, task in zip([2, 1, 3, 5, 4], self.tasks):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
        
        # Projects
        self.project_tasks[4].move(3)
        for order, task in zip([1, 2, 3, 5, 4], self.project_tasks):
            task.refresh_from_db()
            self.assertEqual(task.order, order)
        self.project_tasks[1].move(0)
        for order, task in zip([2, 1, 3, 5, 4], self.project_tasks):
            task.refresh_from_db()
            self.assertEqual(task.order, order)