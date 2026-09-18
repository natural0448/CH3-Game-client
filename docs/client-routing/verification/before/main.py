"""Small village client: Python 3.12, pygame-ce>=2.5,<3, aiohttp>=3.12,<4.

From Chapter3: python Game-client/main.py
From Game-client: python main.py
Install into your selected Python environment:
    python -m pip install 'pygame-ce>=2.5,<3' 'aiohttp>=3.12,<4'
Run `python main.py --check` for an offline configuration/dependency check.

The server must provide the JSON auth contract described in network.py.
Game-server provides these JSON endpoints in game/auth_views.py.
No credentials are saved. Close the window to cancel/close all network work.

Manual acceptance: login -> first WS state -> right -> matching command_id
-> gather at (2,2); 302/401 must not become game state; disconnect disables
input, retries three times at 2s, restores server state without replay.
Check two independent clients, focused login inputs, resize, logout, close.
"""

import argparse
import json
import os
from pathlib import Path
import queue
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from network import NetworkWorker
from state import VillageState


def load_config():
    path = Path(__file__).resolve().with_name("config.json")
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("tile_size", 32) != 32:
        raise ValueError("The server map uses logical tiles of 32 pixels")
    for key, low, high in (("window_width", 640, 3840), ("window_height", 480, 2160), ("fps", 30, 120)):
        value = config.get(key)
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f"Invalid config value: {key}")
    return config


def main():
    parser = argparse.ArgumentParser(description="작은 마을 Pygame 접속기")
    parser.add_argument("--check", action="store_true", help="설정과 의존성만 확인 (서버 연결 없음)")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        print("Python 3.12 환경에서 실행해 주세요.")
        return 1
    import pygame
    from render import Renderer

    config = load_config()
    network = NetworkWorker(config)
    if args.check:
        from importlib.metadata import version
        print(f"Python 3.12 | pygame-ce {version('pygame-ce')} | aiohttp {version('aiohttp')}")
        print("Config OK. No server connection was opened.")
        return 0

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
            renderer.analytics.reset()
            renderer.history.reset()
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
                renderer.analytics.accept(event, state)
                renderer.history.accept(event, state)
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
                    elif hit == "analytics":
                        request = renderer.analytics.request(state)
                        if request is not None:
                            renderer.history.opened = False
                            renderer.api_source = "analytics"
                            renderer.api_scroll = 0
                            if not network.submit(request):
                                renderer.analytics.reset()
                    elif hit == "analytics_close":
                        renderer.analytics.opened = False
                    elif hit in ("analytics_previous", "analytics_next"):
                        renderer.analytics.turn_page(-1 if hit == "analytics_previous" else 1)
                    elif hit == "history":
                        request = renderer.history.request(state)
                        if request is not None:
                            renderer.analytics.opened = False
                            renderer.api_source = "history"
                            renderer.api_scroll = 0
                            if not network.submit(request):
                                renderer.history.reset()
                    elif hit == "history_close":
                        renderer.history.opened = False
                    elif hit in ("history_previous", "history_next"):
                        renderer.history.turn_page(-1 if hit == "history_previous" else 1)
                    elif hit == "api_source" and state.show_delivery_api:
                        sources = ("delivery", "analytics", "history")
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


if __name__ == "__main__":
    raise SystemExit(main())
