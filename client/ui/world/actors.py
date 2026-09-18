"""Actor sprite layer."""
import pygame

from client.contracts.game import TILE
from client.ui.drawing import GREEN, INK


def draw_actors(painter, actors):
    for actor in actors:
        x, y = actor.pixel_x, actor.pixel_y
        pygame.draw.ellipse(painter.canvas, (128, 153, 112), (x + 4, y + 23, 25, 7))
        if "hero" in painter.images:
            hero = painter.images["hero"]
            painter.canvas.blit(hero, hero.get_rect(midbottom=(x + TILE // 2, y + TILE)))
        else:
            pygame.draw.rect(painter.canvas, GREEN, (x + 7, y + 12, 18, 16), border_radius=5)
            pygame.draw.circle(painter.canvas, (255, 227, 185), (x + 16, y + 9), 7)
            pygame.draw.circle(painter.canvas, INK, (x + 19, y + 9), 1)
        pygame.draw.rect(painter.canvas, GREEN if actor.mine else (78, 95, 171),
                         (x + 1, y + 1, 30, 30), 2, border_radius=5)
