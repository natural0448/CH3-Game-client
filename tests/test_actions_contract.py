"""Action snapshot allowlist and unavailable semantics."""
import copy
import unittest

from client.contracts.queries import read_actions
from tests.support import action_snapshot


class ActionContractTests(unittest.TestCase):
    def test_allowlist_keeps_source_unchanged(self):
        data = action_snapshot()
        data["csrfToken"] = "private"
        data["summary"]["cookie"] = "private"
        data["summary"]["by_action"][0]["password"] = "private"
        before = copy.deepcopy(data)
        clean = read_actions(data)
        self.assertNotIn("private", str(clean))
        self.assertEqual(data, before)
        self.assertEqual(clean["summary"]["event_count"], 10)
        self.assertEqual(clean["raw_record_count"], 12)

    def test_unavailable_is_not_measured_zero(self):
        self.assertEqual(read_actions({"available": False, "event_count": 0}),
                         {"available": False, "summary": None})
        data = action_snapshot()
        data["raw_record_count"] = data["summary"]["event_count"] = 0
        data["summary"]["by_action"] = []
        data["summary"]["by_room"] = []
        self.assertEqual(read_actions(data)["summary"]["event_count"], 0)

    def test_wrong_source_and_duplicate_action_are_rejected(self):
        data = action_snapshot()
        data["source_kind"] = "live"
        with self.assertRaises(ValueError):
            read_actions(data)
        data = action_snapshot()
        data["summary"]["by_action"][1] = data["summary"]["by_action"][0]
        with self.assertRaises(ValueError):
            read_actions(data)


if __name__ == "__main__":
    unittest.main()
