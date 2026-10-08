"""Displayed-frame gating, event retries and authenticated event networking."""
import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pygame

from client.application.ads import AdSlot
from client.application.controller import Controller
from client.configuration import load_config
from client.contracts.ads import read_ad_event
from client.network.ads import AdGateway
from client.network.session import AdEventRejected, AuthSession
from client.network.http import JsonHttpClient, ProtocolError
from client.network.worker import NetworkWorker
from client.ui.input import InputRouter
from client.ui.layout import build_layout
from client.ui.renderer import ScreenRenderer
from tests.support import player
from tests.test_ads_feature import NetworkStub, decision, png


def ready_controller():
    controller = Controller(NetworkStub())
    controller.game.apply_identity(player(7))
    controller.game.apply_status("connected", controller.game.epoch)
    controller.game.apply_state(player(7), controller.game.epoch, first=True)
    controller.app.phase = "connected"
    controller.request_ad("village-board", now=0)
    request = controller.network.requests[-1]
    controller.handle_network_event({**request, "kind": "ad", "status": 200,
                                     "decision": decision(), "image_bytes": png(), "message": "ready"})
    return controller


def confirmation(request, created=False):
    kind = request["event_type"]
    return {**request, "status": 200, "ad_event": {
        "event_id": request["decision_id"] + ":" + kind, "event_type": kind, "created": created}}


class EventStateTests(unittest.TestCase):
    def test_permanent_refusal_stops_events_and_allows_new_selection_after_two_seconds(self):
        for status in (400, 403, 404):
            controller = ready_controller();slot = controller.ads.slots["village-board"]
            controller.confirm_ad_display({"village-board": decision()["decision_id"]}, now=0)
            request = controller.network.requests[-1]
            with self.subTest(status=status):
                slot.accept_event({**request, "kind": "ad_event_error", "status": status,
                                   "event_rejected": True, "message": "광고 새 요청 필요"}, 7, 1)
                self.assertTrue(slot.event_rejected)
                self.assertFalse(slot.click_requested)
                self.assertIsNone(slot.request_event("impression", 7, 100))
                self.assertIsNone(slot.request(7, 2.99))
                self.assertIsNotNone(slot.request(7, 3))
                self.assertFalse(slot.event_rejected)

    def test_click_timeout_retries_same_decision_after_another_visible_frame(self):
        controller = ready_controller();slot = controller.ads.slots["village-board"]
        controller.confirm_ad_display({"village-board": decision()["decision_id"]}, now=0)
        slot.accept_event(confirmation(controller.network.requests[-1]), 7, 0)
        controller.request_ad_event("village-board", "click", now=1)
        click = controller.network.requests[-1]
        slot.accept_event({**click, "kind": "ad_event_error", "status": 503, "message": "retry"}, 7, 1)
        self.assertIsNone(slot.request(7, 100))
        count = len(controller.network.requests)
        controller.confirm_ad_display({"village-board": decision()["decision_id"]}, now=2.9)
        self.assertEqual(len(controller.network.requests), count)
        controller.confirm_ad_display({"village-board": decision()["decision_id"]}, now=3)
        self.assertEqual(controller.network.requests[-1]["decision_id"], click["decision_id"])
        self.assertEqual(controller.network.requests[-1]["event_type"], "click")
        slot.accept_event(confirmation(controller.network.requests[-1]), 7, 3)
        controller.confirm_ad_display({"village-board": decision()["decision_id"]}, now=4)
        self.assertEqual(len(controller.network.requests), count + 1)

    def test_lobby_is_displayed_without_sending_classroom_events(self):
        controller = ready_controller()
        controller.request_ad("lobby-banner", now=0)
        request = controller.network.requests[-1]
        lobby_decision = {**decision(), "slot_id": "lobby-banner", "decision_id": "lobby-selection"}
        controller.handle_network_event({**request, "kind": "ad", "status": 200,
                                         "decision": lobby_decision, "image_bytes": png()})
        count = len(controller.network.requests)
        controller.confirm_ad_display({"lobby-banner": "lobby-selection"}, now=0)
        self.assertTrue(controller.ads.slots["lobby-banner"].displayed)
        self.assertEqual(len(controller.network.requests), count)
        self.assertFalse(controller.request_ad_event("lobby-banner", "click", now=20))

    def test_decode_failure_allows_a_fresh_selection_without_an_event(self):
        controller = ready_controller();slot = controller.ads.slots["village-board"]
        self.assertIsNone(slot.request(7, 100))
        controller.confirm_ad_display({}, failures={"village-board": "old-id"}, now=1)
        self.assertFalse(slot.image_failed)
        controller.confirm_ad_display({}, failures={"village-board": decision()["decision_id"]}, now=1)
        self.assertTrue(slot.image_failed)
        self.assertFalse(slot.displayed)
        self.assertIsNotNone(slot.request(7, 15))

    def test_no_request_before_display_then_one_confirmed_impression_and_click(self):
        controller = ready_controller();slot = controller.ads.slots["village-board"]
        self.assertFalse(controller.request_ad_event("village-board", "impression", now=0))
        controller.confirm_ad_display({"village-board": decision()["decision_id"]}, now=0)
        request = controller.network.requests[-1]
        self.assertTrue(slot.impression_pending)
        self.assertFalse(controller.request_ad_event("village-board", "click"))
        controller.confirm_ad_display({"village-board": decision()["decision_id"]}, now=0)
        self.assertEqual(len(controller.network.requests), 2)
        controller.handle_network_event(confirmation(request))
        self.assertTrue(slot.impression_ok)
        self.assertTrue(controller.request_ad_event("village-board", "click"))
        self.assertIsNone(slot.request(7, 20))
        controller.handle_network_event(confirmation(controller.network.requests[-1]))
        self.assertTrue(slot.click_ok)
        self.assertFalse(controller.request_ad_event("village-board", "click"))

    def test_retry_queue_failure_stale_ids_and_new_ad_reset(self):
        controller = ready_controller();slot = controller.ads.slots["village-board"]
        slot.displayed = True
        request = slot.request_event("impression", 7, 0)
        self.assertFalse(slot.accept_event({**confirmation(request), "player_id": 8}, 7, 1))
        self.assertTrue(slot.accept_event({**request, "status": 503, "message": "retry"}, 7, 1))
        self.assertIsNone(slot.request_event("impression", 7, 2.9))
        retry = slot.request_event("impression", 7, 3)
        self.assertTrue(slot.accept_event(confirmation(retry, created=False), 7, 3))
        self.assertTrue(slot.impression_ok)
        slot.request(7, 20)
        self.assertFalse(slot.accept_event(confirmation(retry), 7, 21))
        self.assertFalse(slot.impression_ok)
        controller = ready_controller();slot = controller.ads.slots["village-board"];slot.displayed = True
        controller.network.submit = lambda request: False
        self.assertFalse(controller.request_ad_event("village-board", "impression", now=0))
        self.assertFalse(slot.impression_pending);self.assertEqual(slot.event_retry_at, 2)

    def test_event_contract_rejects_unsafe_confirmation(self):
        valid = {"event_id": "d1:click", "event_type": "click", "created": False}
        self.assertEqual(read_ad_event({**valid, "secret": "excluded"}, "d1", "click"), valid)
        for bad in [{**valid, "created": "False"}, {**valid, "event_id": "other:click"}, None]:
            with self.assertRaises(ValueError):read_ad_event(bad, "d1", "click")

    def test_only_current_authentication_failure_clears_ad_and_logs_out(self):
        controller = ready_controller()
        controller.confirm_ad_display({"village-board": decision()["decision_id"]})
        request = controller.network.requests[-1]
        failure = {**request, "kind": "ad_event_error", "status": 401,
                   "needs_login": True, "message": "다시 로그인하세요."}
        controller.handle_network_event({**failure, "request_id": "old-selection"})
        self.assertEqual(controller.app.phase, "connected")
        controller.handle_network_event(failure)
        self.assertEqual(controller.network.requests[-1], {"kind": "logout"})
        self.assertEqual(controller.app.phase, "logging_out")
        self.assertTrue(all(slot.status == "idle" for slot in controller.ads.slots.values()))
        controller.handle_network_event({"kind": "logged_out", "message": "정리 완료"})
        self.assertIsNone(controller.game.own)
        self.assertEqual(controller.app.phase, "signed_out")


class EventUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init();pygame.font.init();pygame.display.set_mode((1100, 880))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_image_failure_hidden_panel_and_minimized_have_no_receipts(self):
        controller = ready_controller();layout = build_layout((1100, 880))
        renderer = ScreenRenderer(pygame.display.get_surface(), load_config())
        controller.ads.slots["village-board"].image_bytes = b"broken"
        self.assertEqual(renderer.render(controller.screen_model(), layout, 60), {})
        controller.ads.slots["village-board"].image_bytes = png()
        controller.queries.slots["history"].opened = True
        self.assertEqual(renderer.render(controller.screen_model(), layout, 60), {})
        controller.queries.slots["history"].opened = False
        with patch("pygame.display.get_active", return_value=False):
            self.assertEqual(renderer.render(controller.screen_model(), layout, 60), {})
        receipt = renderer.render(controller.screen_model(), layout, 60)
        self.assertIn("village-board", receipt)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=layout.ad_cards["village-board"].center)
        self.assertEqual(InputRouter().route(event, layout, controller.app, controller.queries),
                         {"kind": "ad_click", "slot_id": "village-board"})
        with patch("pygame.display.get_active", return_value=False):
            self.assertNotEqual(InputRouter().route(event, layout, controller.app, controller.queries),
                                {"kind": "ad_click", "slot_id": "village-board"})


class EventNetworkTests(unittest.IsolatedAsyncioTestCase):
    async def test_auth_session_distinguishes_permanent_rejection_and_transient_failure(self):
        for status in (302, 400, 401, 403, 404, 503):
            auth = AuthSession(load_config())
            async def refresh_csrf(): pass
            async def request_json(*args, **kwargs):
                raise ProtocolError("fixture", status)
            auth.refresh_csrf = refresh_csrf;auth.request_json = request_json
            expected = AdEventRejected if status != 503 else ProtocolError
            with self.subTest(status=status), self.assertRaises(expected) as caught:
                await auth.post_ad_event("d1", "impression")
            self.assertEqual(caught.exception.status, status)
            self.assertEqual(getattr(caught.exception, "event_rejected", False), status != 503)

    async def test_http_error_body_exposes_only_known_public_reasons(self):
        class Content:
            async def read(self, size):
                return self.raw[:size]
        class Response:
            status = 400
            content_type = "application/json"
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
        response = Response();response.content = Content()
        session = SimpleNamespace(closed=False, request=lambda *args, **kwargs: response)
        http = JsonHttpClient(session, "http://fixture", 3, "http://fixture")
        for raw, code in ((b'{"error":"decision_snapshot_missing"}', "decision_snapshot_missing"),
                          (b'{"error":"private trace"}', None), (b'{"error":[]}', None), (b'{', None)):
            response.content.raw = raw
            with self.subTest(code=code), self.assertRaises(ProtocolError) as caught:
                await http.request_json("POST", "/api/ads/events/", payload={})
            self.assertEqual(caught.exception.status, 400)
            self.assertEqual(caught.exception.error_code, code)
            self.assertNotIn("private trace", str(caught.exception))

    async def test_gateway_permanent_refusal_clears_selection_cooldown(self):
        async def post_ad_event(*args):
            raise AdEventRejected("광고 새 요청 필요", 400)
        events=[];gateway=AdGateway(SimpleNamespace(post_ad_event=post_ad_event),
                                   lambda kind,**data:events.append((kind,data)))
        gateway.set_identity(SimpleNamespace(player_id=7))
        gateway.last_requested["village-board"] = 100
        await gateway.fetch_event({"slot_id":"village-board","request_id":"r1","player_id":7,
                                   "decision_id":"d1","event_type":"impression"})
        self.assertTrue(events[0][1]["event_rejected"])
        self.assertNotIn("village-board", gateway.last_requested)
        await gateway.close()

    async def test_current_session_csrf_and_public_duplicate_receipt(self):
        calls=[]
        async def refresh_csrf():calls.append("csrf")
        async def request_json(method, path, **kwargs):
            calls.append((method, path, kwargs));return {"event_id":"d1:impression","event_type":"impression","created":False}
        events=[];auth=AuthSession(load_config())
        auth.refresh_csrf=refresh_csrf;auth.request_json=request_json
        gateway=AdGateway(auth,lambda kind,**data:events.append((kind,data)))
        gateway.set_identity(SimpleNamespace(player_id=7))
        await gateway.fetch_event({"slot_id":"village-board","request_id":"r1","player_id":7,"decision_id":"d1","event_type":"impression"})
        self.assertEqual(calls[0],"csrf")
        self.assertEqual(calls[1],('POST','/api/ads/events/',{'payload':{'decision_id':'d1','event_type':'impression'},'csrf':True}))
        self.assertEqual(events[0][0],"ad_event");self.assertEqual(events[0][1]['status'],200)
        self.assertFalse(events[0][1]['ad_event']['created'])
        await gateway.close()

    async def test_event_401_uses_lesson_error_result_and_login_flag(self):
        async def post_ad_event(decision_id, event_type):
            raise ProtocolError("다시 로그인하세요.", 401)
        events=[]
        gateway=AdGateway(SimpleNamespace(post_ad_event=post_ad_event),
                          lambda kind,**data:events.append((kind,data)))
        gateway.set_identity(SimpleNamespace(player_id=7))
        await gateway.fetch_event({"slot_id":"village-board","request_id":"r1","player_id":7,
                                   "decision_id":"d1","event_type":"impression"})
        self.assertEqual(events[0][0], "ad_event_error")
        self.assertTrue(events[0][1]["needs_login"])
        self.assertEqual(events[0][1]["decision_id"], "d1")
        await gateway.close()

    async def test_busy_worker_returns_correlated_error_instead_of_dropping_request(self):
        class Component:
            def __init__(self,*args):pass
            async def close(self):pass
            async def check_timeout(self):pass
            def start_event(self,request):return False
        with patch('client.network.worker.AuthSession',Component), patch('client.network.worker.PlayChannel',Component), \
                patch('client.network.worker.QueryGateway',Component), patch('client.network.worker.AdGateway',Component):
            worker=NetworkWorker({})
            request={'kind':'ad_event','slot_id':'village-board','request_id':'r1','player_id':7,'decision_id':'d1','event_type':'impression'}
            worker.submit(request);task=asyncio.create_task(worker._run())
            for _ in range(30):
                await asyncio.sleep(.01)
                if not worker.events.empty():break
            result=worker.events.get_nowait();worker._stop.set();await task
        for key in ('slot_id','request_id','player_id','decision_id','event_type'):self.assertEqual(result[key],request[key])
        self.assertIsNone(result['status']);self.assertEqual(result['kind'],'ad_event_error')
