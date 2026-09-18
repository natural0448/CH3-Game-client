"""Executable entry point: run from Game-client with `python client/main.py`."""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from client.configuration import load_config
from client.network.worker import NetworkWorker


def main():
    parser = argparse.ArgumentParser(description="작은 마을 Pygame 접속기")
    parser.add_argument("--check", action="store_true", help="설정과 의존성만 확인 (서버 연결 없음)")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        print("Python 3.12 환경에서 실행해 주세요.")
        return 1
    config = load_config()
    if args.check:
        NetworkWorker(config)
        from importlib.metadata import version
        print(f"Python 3.12 | pygame-ce {version('pygame-ce')} | aiohttp {version('aiohttp')}")
        print("Config OK. No server connection was opened.")
        return 0
    from client.app import run
    return run(config)


if __name__ == "__main__":
    raise SystemExit(main())
