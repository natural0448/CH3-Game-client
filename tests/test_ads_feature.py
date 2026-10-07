"""Ad retention, credential-free contracts, same-origin PNG fetch and visible rendering."""
import asyncio
import os
import struct
import unittest
import zlib
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from client.application.ads import AdStore
from client.application.controller import Controller
from client.configuration import load_config
from client.contracts.ads import read_decision
from client.network.ads import AdGateway
from client.ui.input import InputRouter
from client.ui.layout import build_layout
from client.ui.renderer import ScreenRenderer
from tests.support import Response, player


def png():
    def chunk(name, body):
        return struct.pack(">I", len(body)) + name + body + struct.pack(">I", zlib.crc32(name + body))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"\x00\x40\x90\x40\xff")) + chunk(b"IEND", b"")


def decision():
    return {"decision_id": "00000000-0000-4000-8000-000000000001", "campaign_id": "forest-tools",
            "title": "숲 도구점", "body": "마을의 도구", "slot_id": "village-board",
            "creative_path": "/static/ads/creatives/forest-tools.png", "bid_amount": 30,
            "policy_version": "highest-bid/v1"}


class NetworkStub:
    def __init__(self):
        self.requests = []

    def submit(self, request):
        self.requests.append(dict(request))
        return True


class AdStateTests(unittest.TestCase):
    def test_retention_stale_identity_and_display_receipt(self):
        store = AdStore();slot = store.slots["village-board"]
        request = slot.request(7, 0)
        event = {**request, "status": 200, "decision": decision(), "image_bytes": png(), "message": "ready"}
        self.assertFalse(slot.accept({**event, "player_id": 8}, 7))
        self.assertTrue(slot.accept(event, 7))
        self.assertIsNone(slot.request(7, 14.9))
        store.mark_displayed({"village-board": "older-decision"})
        self.assertFalse(slot.displayed)
        store.mark_displayed({"village-board": decision()["decision_id"]})
        self.assertTrue(slot.displayed)
        self.assertIsNotNone(slot.request(7, 15))
        self.assertFalse(slot.accept(event, 7))
        store.reset();self.assertIsNone(slot.decision)

    def test_public_contract_and_unsafe_values(self):
        clean = read_decision({**decision(), "media_key": "excluded", "cookie": "excluded"}, "village-board")
        self.assertNotIn("media_key", clean);self.assertNotIn("cookie", clean)
        self.assertIsNone(read_decision({"ad": None}, "village-board"))
        for changes in [{"bid_amount": True}, {"creative_path": "http://other/image.png"}, {"slot_id": "lobby-banner"}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                read_decision({**decision(), **changes}, "village-board")


class AdNetworkTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_session_csrf_post_and_same_origin_png(self):
        calls=[]
        class Session:
            def get(self, url, **options):
                calls.append((url, options))
                return Response(content_type="image/png", raw=png())
        async def request_json(method, path, **kwargs):
            calls.append((method, path, kwargs));return decision()
        auth=SimpleNamespace(request_json=request_json, session=Session(), base_url="http://localhost:8000")
        events=[];gateway=AdGateway(auth,lambda kind,**data:events.append((kind,data)))
        gateway.set_identity(SimpleNamespace(player_id=7))
        await gateway.fetch({"slot_id":"village-board","player_id":7,"request_id":"r1"})
        self.assertEqual(calls[0],('POST','/api/ads/decision/',{'payload':{'slot_id':'village-board'},'csrf':True}))
        self.assertEqual(calls[1][0],'http://localhost:8000/static/ads/creatives/forest-tools.png')
        self.assertFalse(calls[1][1]['allow_redirects'])
        self.assertEqual(events[0][1]['image_bytes'],png())
        await gateway.close()

    async def test_logout_suppresses_late_response_and_untrusted_png_path(self):
        started=asyncio.Event();release=asyncio.Event()
        async def request_json(*args,**kwargs):
            started.set();await release.wait();return {'ad':None}
        auth=SimpleNamespace(request_json=request_json)
        events=[];gateway=AdGateway(auth,lambda kind,**data:events.append(data))
        gateway.set_identity(SimpleNamespace(player_id=7))
        task=asyncio.create_task(gateway.fetch({'slot_id':'village-board','player_id':7,'request_id':'r1'}))
        await started.wait();await gateway.close();release.set();await task
        self.assertEqual(events,[])
        with self.assertRaises(ValueError):await gateway.fetch_png('http://other/image.png')


class AdUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init();pygame.font.init();pygame.display.set_mode((1100,880))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_same_layout_refresh_and_image_decode_failure_not_displayed(self):
        controller=Controller(NetworkStub());controller.game.apply_identity(player(7));controller.app.phase='connected'
        controller.request_ad('village-board',now=0)
        request=controller.network.requests[-1]
        controller.handle_network_event({**request,'kind':'ad','status':200,'decision':decision(),'image_bytes':b'broken'})
        renderer=ScreenRenderer(pygame.display.get_surface(),load_config())
        receipts=renderer.render(controller.screen_model(),build_layout((1100,880)),60)
        self.assertNotIn('village-board',receipts)
        controller.ads.slots['village-board'].image_bytes=png()
        receipts=renderer.render(controller.screen_model(),build_layout((1100,880)),60)
        self.assertEqual(receipts['village-board'],decision()['decision_id'])
        controller.ads.mark_displayed(receipts)
        self.assertTrue(controller.ads.slots['village-board'].displayed)
        layout=build_layout((1100,880));position=layout.controls['ad_village_refresh'].center
        event=pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=position)
        intent=InputRouter().route(event,layout,controller.app,controller.queries)
        self.assertEqual(intent,{'kind':'ad_refresh','slot_id':'village-board'})
