from mixer.backend.django import mixer
from django.test import TestCase
from core.models import User, Slot

class SlotCreationTests(TestCase):

    def test_can_create_slot(self):
        slot = Slot.objects.create(name="Slot 1", user=mixer.blend(User))
        self.assertNotEqual(slot.id, 1)
        self.assertEqual(slot.order, 1)
    

    def test_making_extra_slots_increases_order(self):
        user1, user2 = mixer.blend(User), mixer.blend(User)
        slot = mixer.blend(Slot, user=user1, order=None)
        self.assertEqual(slot.order, 1)
        slot = mixer.blend(Slot, user=user1, order=None)
        self.assertEqual(slot.order, 2)
        slot = mixer.blend(Slot, user=user2, order=None)
        self.assertEqual(slot.order, 1)
        slot = mixer.blend(Slot, user=user1, order=None)
        self.assertEqual(slot.order, 3)
        slot = mixer.blend(Slot, user=user2, order=None)
        self.assertEqual(slot.order, 2)
    

    def test_can_specify_slot_order(self):
        slot = mixer.blend(Slot, order=10)
        self.assertEqual(slot.order, 10)
    

    def test_order_only_set_on_creation(self):
        user1 = mixer.blend(User)
        slot = mixer.blend(Slot, user=user1, order=None)
        self.assertEqual(slot.order, 1)
        mixer.blend(Slot, user=user1, order=None)
        mixer.blend(Slot, user=user1, order=None)
        slot.name = "S"
        slot.save()
        slot.refresh_from_db()
        self.assertEqual(slot.order, 1)



class SlotOrderTests(TestCase):

    def test_slot_ordered_by_order(self):
        user = mixer.blend(User)
        slot1 = mixer.blend(Slot, user=user, order=1)
        slot2 = mixer.blend(Slot, user=user, order=3)
        slot3 = mixer.blend(Slot, user=user, order=2)
        self.assertEqual(list(Slot.objects.all()), [slot1, slot3, slot2])



class SlotMovingTests(TestCase):

    def test_can_move_to_current_position(self):
        user = mixer.blend(User)
        slots = [
            mixer.blend(Slot, user=user, order=1),
            mixer.blend(Slot, user=user, order=2),
            mixer.blend(Slot, user=user, order=3),
            mixer.blend(Slot, user=user, order=4),
            mixer.blend(Slot, user=user, order=5),
        ]
        mixer.blend(Slot)
        slots[2].move_to(2)
        slots[2].refresh_from_db()
        self.assertEqual(slots[2].order, 3)
    

    def test_can_move_to_right(self):
        user = mixer.blend(User)
        slots = [
            mixer.blend(Slot, user=user, order=1),
            mixer.blend(Slot, user=user, order=2),
            mixer.blend(Slot, user=user, order=3),
            mixer.blend(Slot, user=user, order=4),
            mixer.blend(Slot, user=user, order=5),
        ]
        mixer.blend(Slot)
        with self.assertNumQueries(2):
            slots[1].move_to(3)
        for slot in slots: slot.refresh_from_db()
        self.assertEqual(slots[0].order, 1)
        self.assertEqual(slots[1].order, 4)
        self.assertEqual(slots[2].order, 2)
        self.assertEqual(slots[3].order, 3)
        self.assertEqual(slots[4].order, 5)
    

    def test_can_move_to_left(self):
        user = mixer.blend(User)
        slots = [
            mixer.blend(Slot, user=user, order=1),
            mixer.blend(Slot, user=user, order=2),
            mixer.blend(Slot, user=user, order=3),
            mixer.blend(Slot, user=user, order=4),
            mixer.blend(Slot, user=user, order=5),
        ]
        mixer.blend(Slot)
        with self.assertNumQueries(2):
            slots[4].move_to(0)
        for slot in slots: slot.refresh_from_db()
        self.assertEqual(slots[0].order, 2)
        self.assertEqual(slots[1].order, 3)
        self.assertEqual(slots[2].order, 4)
        self.assertEqual(slots[3].order, 5)
        self.assertEqual(slots[4].order, 1)