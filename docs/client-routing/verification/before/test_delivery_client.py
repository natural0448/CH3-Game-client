"""Offline delivery HTTP contract and main-thread state checks."""
import asyncio
import json
import unittest
from unittest.mock import patch

from network import NetworkWorker
from state import VillageState


class Response:
    def __init__(self, status=200, content_type="application/json", data=None, raw=None):
        self.status, self.content_type = status, content_type
        self.raw = raw if raw is not None else json.dumps(data).encode()
        self.content = self
        self.body_read = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def iter_chunked(self, size):
        self.body_read = True
        yield self.raw


class Session:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.response


class DeliveryNetworkTests(unittest.IsolatedAsyncioTestCase):
    def worker(self, response):
        worker = NetworkWorker({"server_base_url":"http://127.0.0.1:8000"})
        worker.identity = 7
        worker.session = Session(response)
        return worker

    async def test_whitelisted_result_same_session_and_five_second_limit(self):
        response = Response(data={"event_count":12, "pending_publish_count":3,
                                  "source":"mysql-outbox", "password":"excluded", "csrfToken":"excluded"})
        worker = self.worker(response)
        session = worker.session
        worker.pending = "game-command"
        with patch("network.time.monotonic", return_value=100):
            await worker._delivery()
        event = worker.events.get_nowait()
        self.assertEqual(event["json"], {"event_count":12, "pending_publish_count":3, "source":"mysql-outbox"})
        self.assertEqual(event["status"], 200)
        self.assertEqual(event["path"], "GET /api/delivery/")
        self.assertIs(worker.session, session)
        self.assertEqual(worker.pending, "game-command")
        args, kwargs = session.calls[0]
        self.assertEqual(args, ("GET", "http://127.0.0.1:8000/api/delivery/"))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["timeout"].total, 8)
        with patch("network.time.monotonic", return_value=104.99):
            await worker._delivery()
        self.assertEqual(len(session.calls), 1)
        self.assertIsNone(worker.events.get_nowait()["json"])
        with patch("network.time.monotonic", return_value=105):
            await worker._delivery()
        self.assertEqual(len(session.calls), 2)

    async def test_redirect_unauthorized_and_html_never_parse_body(self):
        for status in (302, 401, 200):
            with self.subTest(status=status):
                response = Response(status=status, content_type="text/html", raw=b"<html>private</html>")
                worker = self.worker(response)
                await worker._delivery()
                event = worker.events.get_nowait()
                self.assertFalse(response.body_read)
                self.assertEqual(event["status"], status)
                self.assertIsNone(event["json"])
                self.assertNotIn("private", str(event))
                if status in (302, 401):
                    self.assertIn("로그인", event["message"])

    async def test_invalid_counts_source_json_and_timeout(self):
        for data in ({"event_count":True, "pending_publish_count":0, "source":"mysql-outbox"},
                     {"event_count":1, "pending_publish_count":-1, "source":"mysql-outbox"},
                     {"event_count":1, "pending_publish_count":0, "source":"private-token"}):
            worker = self.worker(Response(data=data))
            await worker._delivery()
            self.assertIsNone(worker.events.get_nowait()["json"])
        worker = self.worker(Response(raw=b"invalid-json"))
        await worker._delivery()
        self.assertIsNone(worker.events.get_nowait()["json"])
        async def timeout(*args):
            raise asyncio.TimeoutError()
        worker._json = timeout
        worker.delivery_sent_at = float("-inf")
        await worker._delivery()
        self.assertIn("실패", worker.events.get_nowait()["message"])

    async def test_slow_delivery_does_not_block_command_queue_and_is_cancelled_on_close(self):
        worker = self.worker(Response(data={}))
        started, moved, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()
        async def slow_delivery():
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
        async def command(request):
            moved.set()
        async def close_session():
            pass
        worker._delivery, worker._command = slow_delivery, command
        worker.session.close = close_session
        worker.session.cookie_jar = type("Jar", (), {"clear":lambda self:None})()
        task = asyncio.create_task(worker._run())
        try:
            worker.submit({"kind":"delivery"})
            await asyncio.wait_for(started.wait(), 1)
            worker.submit({"kind":"command"})
            await asyncio.wait_for(moved.wait(), 1)
            self.assertFalse(cancelled.is_set())
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        self.assertTrue(cancelled.is_set())
        self.assertIsNone(worker.session)


class DeliveryStateTests(unittest.TestCase):
    def test_click_gating_result_isolation_and_logout_cleanup(self):
        state = VillageState()
        self.assertIsNone(state.request_delivery(now=10))
        state.own = {"player_id":7, "coins":4}
        state.phase = "connected"
        state.pending = "move-uuid"
        self.assertEqual(state.request_delivery(now=10), {"kind":"delivery"})
        self.assertIsNone(state.request_delivery(now=20))  # Still in flight.
        state.accept(dict(kind="delivery", player_id=7, path="GET /api/delivery/", status=200,
                          json={"event_count":12,"pending_publish_count":3,"source":"mysql-outbox"}, message="done"))
        self.assertEqual(state.own["coins"], 4)
        self.assertEqual(state.pending, "move-uuid")
        self.assertIsNone(state.request_delivery(now=14.99))
        self.assertIsNotNone(state.request_delivery(now=15))
        state.clear_account()
        state.accept(dict(kind="delivery", player_id=7))  # Ignore a late result.
        self.assertIsNone(state.delivery)
        self.assertFalse(state.delivery_busy)


if __name__ == "__main__":
    unittest.main()
