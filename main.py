"""Compatibility entry point for `python main.py`."""
from client.main import main


if __name__ == "__main__":
    raise SystemExit(main())
