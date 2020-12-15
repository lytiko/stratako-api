from datetime import date
from mixer.backend.django import mixer
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import *

class OperationCreationTests(TestCase):

    def test_operation_auto_add_order_if_not_given(self):
        slot = mixer.blend(Slot, operation=None)
        operation = mixer.blend(Operation, order=None, slot=slot, started=None)
        self.assertEqual(operation.order, 1)
        operation = mixer.blend(Operation, order=None, slot=slot, started=None)
        self.assertEqual(operation.order, 2)
        operation = mixer.blend(Operation, order=None, slot=slot, started=None)
        self.assertEqual(operation.order, 3)


    def test_order_is_none_if_started(self):
        slot = mixer.blend(Slot, operation=None)
        operation = mixer.blend(Operation, order=None, started="2000-01-01", slot=slot)
        self.assertEqual(operation.order, None)
        operation = mixer.blend(Operation, order=1, started="2000-01-01", slot=slot)
        self.assertEqual(operation.order, None)
    

    def test_order_ignores_started_tasks(self):
        slot = mixer.blend(Slot, operation=None)
        mixer.blend(Operation, slot=slot, started="2000-01-01")
        mixer.blend(Operation, slot=slot, started="2000-01-02")
        operation = mixer.blend(Operation, order=None, slot=slot, started=None)
        self.assertEqual(operation.order, 1)
        operation = mixer.blend(Operation, order=None, slot=slot, started=None)
        self.assertEqual(operation.order, 2)
        operation = mixer.blend(Operation, order=None, slot=slot, started=None)
        self.assertEqual(operation.order, 3)
    

    def test_operations_can_take_custom_order(self):
        slot = mixer.blend(Slot, operation=None)
        operation = mixer.blend(Operation, order=10, slot=slot, started=None)
        self.assertEqual(operation.order, 10)
    

    def test_operation_order_can_be_edited(self):
        slot = mixer.blend(Slot, operation=None)
        operation = mixer.blend(Operation, slot=slot, order=None, started=None)
        self.assertEqual(operation.order, 1)
        operation.order = 10
        operation.save()
        self.assertEqual(operation.order, 10)
        operation.name = "XYZ"
        operation.save()
        self.assertEqual(operation.order, 10)



class OperationOrderTests(TestCase):

    def test_operations_ordered_by_started(self):
        slot = mixer.blend(Slot, operation=None)
        op1 = mixer.blend(Operation, slot=slot, started="2000-01-01")
        op3 = mixer.blend(Operation, slot=slot, started="2000-01-03")
        op2 = mixer.blend(Operation, slot=slot, started="2000-01-02")
        self.assertEqual(list(Operation.objects.all()), [op1, op2, op3])
    

    def test_operations_ordered_by_order(self):
        slot = mixer.blend(Slot, operation=None)
        op1 = mixer.blend(Operation, slot=slot, order=1, started=None)
        op3 = mixer.blend(Operation, slot=slot, order=3, started=None)
        op2 = mixer.blend(Operation, slot=slot, order=2, started=None)
        self.assertEqual(list(Operation.objects.all()), [op1, op2, op3])
    

    def test_operations_ordered_by_started_then_order(self):
        slot = mixer.blend(Slot, operation=None)
        op1 = mixer.blend(Operation, slot=slot, started="2000-01-01")
        op4 = mixer.blend(Operation, slot=slot, order=1, started=None)
        op3 = mixer.blend(Operation, slot=slot, started="2000-01-03")
        op6 = mixer.blend(Operation, slot=slot, order=3, started=None)
        op2 = mixer.blend(Operation, slot=slot, started="2000-01-02")
        op5 = mixer.blend(Operation, slot=slot, order=2, started=None)
        self.assertEqual(list(Operation.objects.all()), [op1, op2, op3, op4, op5, op6])