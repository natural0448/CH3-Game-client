"""Offline regression tests: python -m unittest test_multiplayer -v."""
import asyncio
import json
import unittest
from types import SimpleNamespace

import aiohttp

from network import NetworkWorker
from state import VillageState


def player(pid=1, **changes):
    return {"type": "state", "player_id": pid, "room_id": "room-01",
            "x": 0, "y": 0, "coins": 0, "version": 0, **changes}


class MultiplayerStateTests(unittest.TestCase):
    def setUp(self):
        self.state = VillageState()
        self.state.accept({"kind":"identity", "data":player()})
        self.state.accept({"kind":"status", "phase":"connecting", "epoch":1, "message":"wait"})
        self.state.accept({"kind":"state", "data":player(), "epoch":1, "first":True})

    def snapshot(self, *players, epoch=1):
        self.state.accept({"kind":"snapshot", "epoch":epoch,
                           "data":{"type":"snapshot", "players":list(players)}})

    def test_join_move_and_departure(self):
        self.snapshot(player(), player(2))
        self.assertEqual(set(self.state.players), {1,2})
        self.state.accept({"kind":"state", "epoch":1, "data":player(2,x=4,version=1)})
        self.assertEqual(self.state.players[2]["x"],4)
        self.assertEqual(self.state.own["x"],0)
        self.snapshot(player())
        self.assertEqual(set(self.state.players),{1})

    def test_snapshot_and_other_players_never_ack_my_command(self):
        request = self.state.command("move","right",now=1)
        pending = request["command"]["command_id"]
        self.snapshot(player(x=9,version=9),player(2,version=99))
        self.assertEqual(self.state.own["x"],0)
        self.assertEqual(self.state.players[1]["x"],0)
        self.state.accept({"kind":"state","epoch":1,"data":player(2,version=100,command_id=pending)})
        self.assertEqual(self.state.pending,pending)
        self.state.accept({"kind":"state","epoch":1,"data":player(x=1,version=1,command_id=pending)})
        self.assertIsNone(self.state.pending)
        self.assertEqual(self.state.own["x"],1)

    def test_room_epoch_and_version_boundaries(self):
        self.snapshot(player(),player(2,x=5,version=5),player(3,room_id="room-02"))
        self.assertEqual(set(self.state.players),{1,2})
        self.snapshot(player(),player(2,x=0,version=1))
        self.assertEqual(self.state.players[2]["x"],5)
        self.snapshot(player(),epoch=0)
        self.assertIn(2,self.state.players)
        self.state.accept({"kind":"state","epoch":1,"data":player(3,room_id="room-02")})
        self.assertNotIn(3,self.state.players)
        self.state.accept({"kind":"status","phase":"disconnected","message":"lost","epoch":1})
        self.assertEqual(set(self.state.players),{1})
        self.assertFalse(self.state.ready)
        self.state.accept({"kind":"logged_out","message":"bye"})
        self.assertFalse(self.state.players)

    def test_online_snapshot_disconnect_reconnect_and_error_message(self):
        self.assertIsNone(self.state.online_count)
        self.snapshot(player(), player(2, username="bob"), player(3, room_id="room-02"))
        self.assertEqual(self.state.online_label, "온라인 2명")
        self.state.accept({"kind":"error", "epoch":1, "code":"not_at_gather_tile"})
        error_message = self.state.message
        self.state.accept({"kind":"state", "epoch":1, "data":player(2, version=1, coins=5, username="bob")})
        self.assertEqual(self.state.message, error_message)
        self.assertEqual(self.state.own["coins"], 0)
        self.assertEqual(self.state.players[2]["username"], "bob")
        self.state.accept({"kind":"status", "phase":"disconnected", "epoch":1, "message":"lost"})
        self.assertEqual(self.state.online_label, "온라인 2명 · 마지막 정보")
        self.state.accept({"kind":"status", "phase":"reconnecting", "epoch":2, "message":"retry"})
        self.state.accept({"kind":"state", "epoch":2, "data":player(), "first":True})
        self.assertIn("마지막 정보", self.state.online_label)
        self.snapshot(player(), epoch=1)
        self.assertEqual(self.state.online_count, 2)
        self.snapshot(player(), epoch=2)
        self.assertEqual(self.state.online_label, "온라인 1명")
        self.assertLessEqual(len(self.state.ws_messages), 3)
        self.state.clear_account()
        self.assertIsNone(self.state.online_count)
        self.assertEqual(self.state.ws_messages, [])


class FakeSocket:
    def __init__(self):
        self.incoming = asyncio.Queue()
        self.closed = False

    async def receive(self):
        data = await self.incoming.get()
        return SimpleNamespace(type=aiohttp.WSMsgType.TEXT,data=json.dumps(data))

    async def close(self):
        self.closed = True


class MultiplayerNetworkTests(unittest.IsolatedAsyncioTestCase):
    async def test_worker_forwards_room_members_without_mixing_my_ack_or_version(self):
        worker = NetworkWorker({"server_base_url":"http://127.0.0.1:8000"})
        worker.identity, worker.room_id, worker.version = 1, "room-01", 0
        socket = FakeSocket()
        async def connect(url, **kwargs):
            self.assertEqual(kwargs["origin"],"http://127.0.0.1:8000")
            return socket
        worker.session = SimpleNamespace(ws_connect=connect)
        task = asyncio.create_task(worker._websockets())
        async def deliver(data, kind):
            await socket.incoming.put(data)
            async with asyncio.timeout(2):
                while True:
                    while not worker.events.empty():
                        event = worker.events.get_nowait()
                        if event["kind"] == kind:
                            return event
                    await asyncio.sleep(.001)
        try:
            event = await deliver(player(2,version=90), "state")
            self.assertFalse(event["first"])
            self.assertFalse(worker.ready)
            self.assertEqual(worker.version,0)
            event = await deliver(player(), "state")
            self.assertTrue(event["first"])
            self.assertTrue(worker.ready)
            worker.pending = "my-command"
            event = await deliver({"type":"snapshot", "players":[player(),player(2),player(3,room_id="room-02")]}, "snapshot")
            self.assertEqual([p["player_id"] for p in event["data"]["players"]],[1,2])
            self.assertEqual(worker.pending,"my-command")
            await deliver(player(2,version=99,command_id="my-command"),"state")
            self.assertEqual(worker.pending,"my-command")
            self.assertEqual(worker.version,0)
            await deliver(player(version=1,command_id="my-command"),"state")
            self.assertIsNone(worker.pending)
            self.assertEqual(worker.version,1)
        finally:
            task.cancel()
            await asyncio.gather(task,return_exceptions=True)
            self.assertTrue(socket.closed)


if __name__ == "__main__":
    unittest.main()
