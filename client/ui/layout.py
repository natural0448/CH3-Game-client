"""One immutable logical layout shared by drawing and hit testing."""
from dataclasses import dataclass

import pygame

CANVAS = (1100, 880)


def _controls():
    return {
        "username": pygame.Rect(24, 96, 220, 40),
        "password": pygame.Rect(256, 96, 220, 40),
        "login": pygame.Rect(488, 96, 118, 40),
        "logout": pygame.Rect(618, 96, 118, 40),
        "up": pygame.Rect(830, 312, 92, 42),
        "left": pygame.Rect(728, 364, 92, 42),
        "down": pygame.Rect(830, 364, 92, 42),
        "right": pygame.Rect(932, 364, 92, 42),
        "gather": pygame.Rect(710, 418, 166, 42),
        "train": pygame.Rect(888, 418, 166, 42),
        "history": pygame.Rect(894, 494, 160, 32),
        "delivery": pygame.Rect(366, 724, 282, 30),
        "delivery_api": pygame.Rect(904, 578, 144, 28),
        "analytics": pygame.Rect(366, 690, 88, 28),
        "actions": pygame.Rect(464, 690, 88, 28),
        "ingest": pygame.Rect(560, 690, 88, 28),
        "api_source": pygame.Rect(710, 612, 230, 28),
        "api_up": pygame.Rect(952, 612, 42, 28),
        "api_down": pygame.Rect(1006, 612, 42, 28),
        "analytics_close": pygame.Rect(530, 174, 104, 32),
        "analytics_previous": pygame.Rect(420, 588, 92, 30),
        "analytics_next": pygame.Rect(526, 588, 92, 30),
        "history_close": pygame.Rect(530, 174, 104, 32),
        "history_previous": pygame.Rect(420, 588, 92, 30),
        "history_next": pygame.Rect(526, 588, 92, 30),
        "actions_refresh": pygame.Rect(420, 174, 100, 32),
        "actions_close": pygame.Rect(530, 174, 104, 32),
        "actions_previous": pygame.Rect(420, 588, 92, 30),
        "actions_next": pygame.Rect(526, 588, 92, 30),
        "ingest_refresh": pygame.Rect(386, 174, 134, 32),
        "ingest_close": pygame.Rect(530, 174, 104, 32),
    }


@dataclass(frozen=True)
class Layout:
    screen_size: tuple[int, int]
    controls: dict
    slots: dict
    ad_slots: dict
    world_rect: pygame.Rect
    panel_rect: pygame.Rect

    def viewport(self):
        width, height = self.screen_size
        ratio = min(width / CANVAS[0], height / CANVAS[1])
        size = (max(1, int(CANVAS[0] * ratio)), max(1, int(CANVAS[1] * ratio)))
        return size, ((width - size[0]) // 2, (height - size[1]) // 2)

    def to_canvas(self, position):
        size, offset = self.viewport()
        return ((position[0] - offset[0]) * CANVAS[0] / size[0],
                (position[1] - offset[1]) * CANVAS[1] / size[1])

    def hit_test(self, position, open_panels):
        point = self.to_canvas(position)
        for kind in ("analytics", "history", "actions", "ingest"):
            if kind in open_panels and self.panel_rect.collidepoint(point):
                prefix = kind + "_"
                return next((name for name, rect in self.controls.items()
                             if name.startswith(prefix) and rect.collidepoint(point)), None)
        return next((name for name, rect in self.controls.items()
                     if not name.startswith(("analytics_", "history_", "actions_", "ingest_"))
                     and rect.collidepoint(point)), None)


def build_layout(screen_size):
    return Layout(
        screen_size=screen_size,
        controls=_controls(),
        slots={
            "village-board": pygame.Rect(24, 656, 310, 78),
            "lobby-banner": pygame.Rect(350, 656, 314, 158),
        },
        ad_slots={
            "village-ad-slot": pygame.Rect(40, 740, 278, 58),
            "lobby-ad-slot": pygame.Rect(710, 788, 342, 24),
        },
        world_rect=pygame.Rect(22, 150, 644, 484),
        panel_rect=pygame.Rect(36, 162, 616, 470),
    )
