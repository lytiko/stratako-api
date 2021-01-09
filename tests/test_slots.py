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