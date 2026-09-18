"""Main-thread font and image loading."""
import threading
from pathlib import Path

import pygame

from client.contracts.game import TILE


class AssetStore:
    def __init__(self, config):
        assert threading.current_thread() is threading.main_thread()
        root = Path(__file__).resolve().parents[2]
        assets = root / config.get("assets_dir", "assets")
        self.notice = ""
        font_path = assets / config.get("font_path", "fonts/NotoSansCJKkr-Regular.otf")
        try:
            self.fonts = {size: pygame.font.Font(str(font_path), size)
                          for size in (13, 15, 17, 20, 26, 32)}
        except (OSError, pygame.error):
            self.notice = "한글 폰트 경로를 확인하세요: assets/fonts/NotoSansCJKkr-Regular.otf"
            self.fonts = {size: pygame.font.SysFont("malgungothic,applesdgothicneo,notosanscjkkr", size)
                          for size in (13, 15, 17, 20, 26, 32)}
        self.images = {}
        for name in ("grass", "path", "tree", "house", "hero"):
            try:
                source = pygame.image.load(str(assets / f"{name}.png")).convert_alpha()
                self.images[name] = pygame.transform.scale(source, (TILE, TILE))
            except (OSError, pygame.error):
                self.notice = f"{name}.png 로딩 실패: config.json의 assets_dir 경로를 확인하세요."
