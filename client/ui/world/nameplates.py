"""Player labels above the character layer."""
import pygame

from client.contracts.game import TILE
from client.ui.drawing import INK, WHITE


def draw_nameplates(painter, nameplates):
    for plate in nameplates:
        text = painter.fonts[13].render(plate.label, True, INK)
        max_height = 11 if plate.tile_y == 0 else text.get_height()
        scale = min(1, 636 / max(1, text.get_width()), max_height / text.get_height())
        if scale < 1:
            text = pygame.transform.smoothscale(text, (
                max(1, int(text.get_width() * scale)), max(1, int(text.get_height() * scale))
            ))
        rect = text.get_rect(midbottom=(24 + plate.tile_x * TILE + TILE // 2,
                                        152 + plate.tile_y * TILE - 3))
        rect.x = max(26, min(rect.x, 662 - rect.width))
        pygame.draw.rect(painter.canvas, WHITE, rect.inflate(4, 2), border_radius=3)
        painter.canvas.blit(text, rect)
