from .base import FunctionalTest, TokenFunctionaltest
from core.models import Slot

class SlotQueryTests(TokenFunctionaltest):

    def test_get_slots(self):
        result = self.client.execute("""{ user {
            slots { name order }
        } }""")
        self.assertEqual(result["data"]["user"]["slots"], [
            {"name": "Public Work", "order": 1},
            {"name": "Private Work", "order": 2},
        ])



class SlotMutationTests(TokenFunctionaltest):

    def test_can_create_slot(self):
        result = self.client.execute("""mutation { createSlot(name: "Slot 3") { 
            slot { name order }
        } }""")
        self.assertEqual(result["data"]["createSlot"]["slot"], {
            "name": "Slot 3", "order": 3
        })


    def test_slot_creation_validation(self):
        slots_at_start = Slot.objects.count()

        # Name must be short enough
        self.check_query_error("""mutation { createSlot(
            name: "00001111222233334444555566667777888899990"
        ) { slot { name } } }""", message="40 characters")
        self.assertEqual(Slot.objects.count(), slots_at_start)


    def test_slot_creation_protection(self):
        del self.client.headers["Authorization"]
        self.check_query_error("""mutation { createSlot(name: "name") {
            slot { name }
        } }""", message="Not authorized")
    

    def test_can_edit_slot(self):
        result = self.client.execute("""mutation { updateSlot(id: 1, name: "X") { 
            slot { name order }
        } }""")
        self.assertEqual(result["data"]["updateSlot"]["slot"], {
            "name": "X", "order": 1
        })
    

    def test_slot_editing_validation(self):
        # Slot must exist
        self.check_query_error("""mutation { updateSlot(id: 5, name: "1") {
            slot { name }
        } }""", message="Does not exist")

        # Slot must be user's
        self.check_query_error("""mutation { updateSlot(id: 100, name: "1") {
            slot { name }
        } }""", message="Does not exist")
    

    def test_slot_editing_protection(self):
        del self.client.headers["Authorization"]
        self.check_query_error("""mutation { updateSlot(id: 1, name: "name") {
            slot { name }
        } }""", message="Not authorized")
    

    def test_can_move_slot(self):
        result = self.client.execute("""mutation { moveSlot(id: 1, index: 1) { 
            slot { name order } user { slots { name order } }
        } }""")
        self.assertEqual(result["data"]["moveSlot"]["slot"], {
            "name": "Public Work", "order": 2
        })
        self.assertEqual(result["data"]["moveSlot"]["user"]["slots"], [
            {"name": "Private Work", "order": 1},
            {"name": "Public Work", "order": 2},
        ])
    

    def test_slot_moving_validation(self):
        # Slot must exist
        self.check_query_error("""mutation { moveSlot(id: 5, index: 1) {
            slot { name }
        } }""", message="Does not exist")

        # Slot must be user's
        self.check_query_error("""mutation { moveSlot(id: 100, index: 1) {
            slot { name }
        } }""", message="Does not exist")


    def test_slot_moving_protection(self):
        del self.client.headers["Authorization"]
        self.check_query_error("""mutation { moveSlot(id: 1, index: 1) {
            slot { name }
        } }""", message="Not authorized")