import unittest
from bot_client import MacBotClient

class TestMacBotClient(unittest.TestCase):
    def setUp(self):
        self.bot = MacBotClient()

    def test_process_state_empty(self):
        state = {}
        actions = self.bot.process_state(state)
        self.assertEqual(actions, [])

    def test_process_state_train_worker(self):
        state = {
            "minerals": 50,
            "units": [
                {"id": 1, "type": "Command_Center", "idle": True}
            ]
        }
        actions = self.bot.process_state(state)
        # It mutates locals to decrement minerals, but doesn't affect the input dictionary directly.
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], {"action": "train", "unit_id": 1, "target_type": "worker"})

    def test_process_state_train_worker_not_enough_minerals(self):
        state = {
            "minerals": 49,
            "units": [
                {"id": 1, "type": "Command_Center", "idle": True}
            ]
        }
        actions = self.bot.process_state(state)
        self.assertEqual(actions, [])

    def test_process_state_train_worker_not_idle(self):
        state = {
            "minerals": 50,
            "units": [
                {"id": 1, "type": "Command_Center", "idle": False}
            ]
        }
        actions = self.bot.process_state(state)
        self.assertEqual(actions, [])

    def test_process_state_multiple_bases_minerals_deduction(self):
        state = {
            "minerals": 50,
            "units": [
                {"id": 1, "type": "Command_Center", "idle": True},
                {"id": 2, "type": "Command_Center", "idle": True}
            ]
        }
        actions = self.bot.process_state(state)
        # Should only train 1 worker since minerals will deduct to 0 after the first one
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], {"action": "train", "unit_id": 1, "target_type": "worker"})

    def test_process_state_gather_minerals(self):
        state = {
            "minerals_fields": [
                {"id": 100}
            ],
            "units": [
                {"id": 2, "type": "SCV", "idle": True}
            ]
        }
        actions = self.bot.process_state(state)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], {"action": "gather", "unit_id": 2, "target_id": 100})

    def test_process_state_gather_minerals_not_idle(self):
        state = {
            "minerals_fields": [
                {"id": 100}
            ],
            "units": [
                {"id": 2, "type": "SCV", "idle": False}
            ]
        }
        actions = self.bot.process_state(state)
        self.assertEqual(actions, [])

    def test_process_state_gather_minerals_no_fields(self):
        state = {
            "minerals_fields": [],
            "units": [
                {"id": 2, "type": "SCV", "idle": True}
            ]
        }
        actions = self.bot.process_state(state)
        self.assertEqual(actions, [])

if __name__ == '__main__':
    unittest.main()
