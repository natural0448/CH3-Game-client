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
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from network import NetworkWorker
from configuration import load_config


def main():
    parser = argparse.ArgumentParser(description="작은 마을 Pygame 접속기")
    parser.add_argument("--check", action="store_true", help="설정과 의존성만 확인 (서버 연결 없음)")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        print("Python 3.12 환경에서 실행해 주세요.")
        return 1
    config = load_config()
    if args.check:
        NetworkWorker(config)  # Validate URLs/timeouts without starting the worker.
        from importlib.metadata import version
        print(f"Python 3.12 | pygame-ce {version('pygame-ce')} | aiohttp {version('aiohttp')}")
        print("Config OK. No server connection was opened.")
        return 0

    from app import run
    return run(config)


if __name__ == "__main__":
    raise SystemExit(main())
