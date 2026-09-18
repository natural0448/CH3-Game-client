"""Main-thread input, queue dispatch and application lifetime."""
import queue

import pygame

from network import NetworkWorker
from render import Renderer
from state import VillageState


def run(config):
    network = NetworkWorker(config)
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption("작은 마을 · Game-client")
    screen = pygame.display.set_mode((config["window_width"], config["window_height"]), pygame.RESIZABLE)
    renderer = Renderer(screen, config)
    state = VillageState()
    clock = pygame.time.Clock()
    username, password, focus = "", "", "username"
    pygame.key.start_text_input()
    closing = False
    network.start()

    def action(name):
        request = state.command(name if name in ("gather", "train") else "move", name)
        if request is not None and not network.submit(request):
            # Delivery was never queued. Avoid inventing a state/error acknowledgement.
            state.accept({"kind": "status", "phase": "disconnected",
                          "message": "요청 큐가 가득 찼어요. 로그아웃 후 다시 시도하세요."})

    def login():
        nonlocal password, focus
        if state.phase != "signed_out" or not username.strip() or not password:
            state.message = "아이디와 비밀번호를 모두 입력해 주세요."
            return
        accepted = network.submit({"kind": "login", "username": username.strip(), "password": password})
        password = ""
        if accepted:
            for panel in renderer.query_panels.values():
                panel.reset()
            state.clear_account()
            state.phase = "authenticating"
            state.message = "로그인 확인 중…"
            focus = None
            pygame.key.stop_text_input()

    try:
        while True:
            # Process received JSON before input so disconnect disables controls immediately.
            for _ in range(200):
                try:
                    event = network.events.get_nowait()
                except queue.Empty:
                    break
                state.accept(event)
                for panel in renderer.query_panels.values():
                    panel.accept(event, state)
                if event.get("kind") == "delivery" and state.delivery:
                    state.message = state.delivery["message"]
                if event["kind"] in ("logged_out", "stopped"):
                    username = password = ""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    closing = True
                    password = username = ""
                    network.stop()
                if closing:
                    continue
                if event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((max(320, event.w), max(240, event.h)), pygame.RESIZABLE)
                    renderer.screen = screen
                elif event.type == pygame.TEXTINPUT and focus and state.phase == "signed_out":
                    value = "".join(c for c in event.text if c.isprintable())
                    if focus == "username":
                        username = (username + value)[:150]
                    else:
                        password = (password + value)[:256]
                elif event.type == pygame.KEYDOWN:
                    if focus:
                        if event.key == pygame.K_TAB:
                            focus = "password" if focus == "username" else "username"
                        elif event.key == pygame.K_ESCAPE:
                            focus = None
                            pygame.key.stop_text_input()
                        elif event.key == pygame.K_BACKSPACE:
                            if focus == "username":
                                username = username[:-1]
                            else:
                                password = password[:-1]
                        elif event.key == pygame.K_RETURN:
                            login()
                        continue  # Never dispatch game keys while editing a login field.
                    directions = {pygame.K_UP: "up", pygame.K_DOWN: "down",
                                  pygame.K_LEFT: "left", pygame.K_RIGHT: "right",
                                  pygame.K_SPACE: "gather", pygame.K_x: "train"}
                    if event.key in directions:
                        action(directions[event.key])
                    elif event.key == pygame.K_TAB and state.phase == "signed_out":
                        focus = "username"
                        pygame.key.start_text_input()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    hit = renderer.hit_test(event.pos)
                    if hit in ("username", "password"):
                        focus = hit
                        pygame.key.start_text_input()
                        continue
                    focus = None
                    pygame.key.stop_text_input()
                    if hit == "login":
                        login()
                    elif hit == "logout" and state.own is not None and state.phase != "logging_out":
                        if network.submit({"kind": "logout"}):
                            state.phase = "logging_out"
                            state.message = "로그아웃 확인 중…"
                            password = ""
                    elif hit == "delivery":
                        request = state.request_delivery()
                        if request is not None and not network.submit(request):
                            state.delivery_busy = False
                            state.delivery_sent_at = float("-inf")
                    elif hit == "delivery_api":
                        state.show_delivery_api = not state.show_delivery_api
                    elif hit in renderer.query_panels or hit == "actions_refresh":
                        kind = "actions" if hit == "actions_refresh" else hit
                        panel = renderer.query_panels[kind]
                        request = panel.request(state)
                        if request is not None:
                            for other in renderer.query_panels.values():
                                if other is not panel:
                                    other.opened = False
                            renderer.api_source = kind
                            renderer.api_scroll = 0
                            if not network.submit(request):
                                panel.reset()
                                state.message = "요청 큐가 가득 찼어요. 다시 눌러 주세요."
                    elif hit and "_" in hit and hit.rsplit("_", 1)[0] in renderer.query_panels:
                        kind, operation = hit.rsplit("_", 1)
                        panel = renderer.query_panels[kind]
                        if operation == "close":
                            panel.opened = False
                        elif operation in ("previous", "next"):
                            panel.turn_page(-1 if operation == "previous" else 1)
                    elif hit == "api_source" and state.show_delivery_api:
                        sources = ("delivery", *renderer.query_panels)
                        renderer.api_source = sources[(sources.index(renderer.api_source) + 1) % len(sources)]
                        renderer.api_scroll = 0
                    elif hit in ("api_up", "api_down") and state.show_delivery_api:
                        renderer.api_scroll = max(0, renderer.api_scroll + (-3 if hit == "api_up" else 3))
                    elif hit in ("up", "down", "left", "right", "gather", "train"):
                        action(hit)
            renderer.draw(state, username, password, focus, clock.get_fps(), closing=closing)
            if not network.thread.is_alive():
                break
            clock.tick(config["fps"])  # Frame pacing only; no HTTP/network wait in the UI.
    finally:
        password = username = ""
        network.stop()
        # Keep processing window events while the worker closes its tasks/session.
        while network.thread.is_alive():
            pygame.event.pump()
            renderer.draw(state, "", "", None, clock.get_fps(), closing=True)
            clock.tick(config["fps"])
        network.thread.join(timeout=0)
        pygame.quit()
    return 0
