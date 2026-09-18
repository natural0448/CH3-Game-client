"""Load and validate local display configuration; never store credentials."""
import json
from pathlib import Path


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

