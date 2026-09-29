"""Same-session JSON policy and button-triggered action query."""
import asyncio
import unittest

from client.contracts.auth import Identity
from client.network.http import JsonHttpClient, ProtocolError
from client.network.queries import QueryGateway
from tests.support import Response, Session, action_snapshot, ingest_summary, player


class FakeAuth:
    def __init__(self, response):
        self.session = Session(response)
        self.http = JsonHttpClient(self.session, "http://127.0.0.1:8000", 8, "http://127.0.0.1:8000")

    async def request_json(self, method, path, *, payload=None, csrf=False):
        return await self.http.request_json(method, path, payload=payload)


def analytics_summary(**changes):
    return {
        "available": True,
        "schema_version": 1,
        "generated_at": "2026-09-28T10:00:00+09:00",
        "source": "delta",
        "record_count": 14,
        "event_count": 11,
        "by_action": [{"event_type": "player.moved", "count": 8}],
        "by_room": [{"room_id": "room-01", "count": 11}],
        "cookie": "must not be exposed",
        **changes,
    }


class JsonHttpTests(unittest.IsolatedAsyncioTestCase):
    async def test_redirect_and_html_are_not_read_as_json(self):
        for status in (302, 401, 200):
            response = Response(status=status, content_type="text/html", raw=b"private cookie")
            client = JsonHttpClient(Session(response), "http://127.0.0.1:8000", 8,
                                    "http://127.0.0.1:8000")
            with self.assertRaises(ProtocolError) as error:
                await client.request_json("GET", "/api/analytics/actions/")
            self.assertFalse(response.body_read)
            self.assertNotIn("private", str(error.exception))
            if status in (302, 401):
                self.assertIn("로그인", str(error.exception))


class QueryGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_analytics_get_uses_same_session_and_safe_allowlist(self):
        auth = FakeAuth(Response(data=analytics_summary()))
        events = []
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))

        await gateway.fetch({"kind": "analytics", "request_id": "analytics-id", "player_id": 1})

        args, kwargs = auth.session.calls[0]
        self.assertEqual(args, ("GET", "http://127.0.0.1:8000/api/analytics/"))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["timeout"].total, 8)
        self.assertEqual(events[0]["json"]["source"], "delta")
        self.assertEqual(events[0]["json"]["record_count"], 14)
        self.assertNotIn("cookie", events[0]["json"])

    async def test_actions_get_uses_same_session_and_safe_queue(self):
        auth = FakeAuth(Response(data=action_snapshot()))
        events = []
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))
        self.assertEqual(auth.session.calls, [])
        await gateway.fetch({"kind": "actions", "request_id": "query-id", "player_id": 1})
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["json"]["summary"]["event_count"], 10)
        args, kwargs = auth.session.calls[0]
        self.assertEqual(args, ("GET", "http://127.0.0.1:8000/api/analytics/actions/"))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["timeout"].total, 8)

    async def test_unavailable_and_login_response_are_not_zero(self):
        events = []
        auth = FakeAuth(Response(data={"available": False}))
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))
        await gateway.fetch({"kind": "actions", "request_id": "missing", "player_id": 1})
        self.assertEqual(events[0]["message"], "행동 집계가 아직 없습니다")
        self.assertEqual(events[0]["json"], {"available": False, "summary": None})

        events.clear()
        auth = FakeAuth(Response(status=401, content_type="text/html", raw=b"private"))
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))
        await gateway.fetch({"kind": "actions", "request_id": "login", "player_id": 1})
        self.assertIn("로그인", events[0]["message"])
        self.assertIsNone(events[0]["json"])
        self.assertNotIn("private", str(events[0]))

    async def test_ingest_get_uses_same_session_and_maps_missing_and_errors(self):
        events = []
        auth = FakeAuth(Response(data=ingest_summary()))
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))
        self.assertEqual(auth.session.calls, [])
        await gateway.fetch({"kind": "ingest", "request_id": "ingest-id", "player_id": 1})
        self.assertEqual(events[0]["json"]["record_count"], 12)
        self.assertEqual(events[0]["json"]["event_count"], 10)
        args, kwargs = auth.session.calls[0]
        self.assertEqual(args, ("GET", "http://127.0.0.1:8000/api/analytics/ingest/"))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["timeout"].total, 8)

        events.clear()
        auth = FakeAuth(Response(data={
            "available": False, "reason": "ingest_summary_not_created",
        }))
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))
        await gateway.fetch({"kind": "ingest", "request_id": "missing", "player_id": 1})
        self.assertIn("준비되지", events[0]["message"])
        self.assertNotIn("record_count", events[0]["json"])

        for status, expected in ((503, "마지막 수집 통계를 읽을 수 없음"), (401, "로그인")):
            events.clear()
            auth = FakeAuth(Response(status=status, content_type="text/html", raw=b"private"))
            gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
            gateway.set_identity(Identity(1, "room-01", 0, player()))
            await gateway.fetch({"kind": "ingest", "request_id": str(status), "player_id": 1})
            self.assertIn(expected, events[0]["message"])
            self.assertIsNone(events[0]["json"])
            self.assertNotIn("private", str(events[0]))


if __name__ == "__main__":
    unittest.main()
