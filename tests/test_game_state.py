"""Authoritative state, room boundary and command correlation."""
import unittest

from client.model.game import GameState
from tests.support import player


class GameStateTests(unittest.TestCase):
    def setUp(self):
        self.game = GameState()
        self.game.apply_identity(player())
        self.game.apply_status("connecting", 1)
        self.game.apply_state(player(), 1, first=True)

    def test_other_players_and_snapshot_never_ack_my_command(self):
        self.assertTrue(self.game.apply_snapshot({"players": [player(), player(2)]}, 1))
        request = self.game.command("move", "right", now=1)
        pending = request["command"]["command_id"]
        self.game.apply_state(player(2, x=4, version=1, command_id=pending), 1)
        self.assertEqual(self.game.pending, pending)
        self.assertEqual(self.game.own["x"], 0)
        result = self.game.apply_state(player(x=1, version=1, command_id=pending), 1)
        self.assertEqual(result["completed_action"], "move")
        self.assertIsNone(self.game.pending)
        self.assertEqual(self.game.own["x"], 1)

    def test_room_version_epoch_disconnect_and_no_replay(self):
        self.game.apply_snapshot({"players": [player(), player(2, x=5, version=5),
                                               player(3, room_id="room-02")]}, 1)
        self.assertEqual(set(self.game.players), {1, 2})
        self.game.apply_snapshot({"players": [player(), player(2, x=0, version=1)]}, 1)
        self.assertEqual(self.game.players[2]["x"], 5)
        request = self.game.command("move", "right", now=1)
        self.assertIsNotNone(request)
        self.assertTrue(self.game.apply_status("disconnected", 1))
        self.assertIsNone(self.game.pending)
        self.assertIsNotNone(self.game.abandoned)
        self.assertFalse(self.game.ready)

    def test_training_requires_tile_and_matching_ack(self):
        self.assertIsNone(self.game.command("train", now=1))
        self.game.own.update(x=3, y=2)
        self.game.players[1] = self.game.own.copy()
        request = self.game.command("train", now=1)
        command_id = request["command"]["command_id"]
        self.assertEqual(set(request["command"]), {"type", "command_id"})
        self.assertFalse(self.game.apply_state(player(x=3, y=2, coins=1, version=1,
                                                      command_id="unrelated"), 1)["accepted"])
        self.assertEqual(self.game.own["coins"], 0)
        result = self.game.apply_state(player(x=3, y=2, coins=1, version=1,
                                              command_id=command_id), 1)
        self.assertEqual(result["completed_action"], "train")
        self.assertEqual(self.game.own["coins"], 1)


if __name__ == "__main__":
    unittest.main()
