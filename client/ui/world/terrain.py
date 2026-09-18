"""Terrain layer."""
import pygame

from client.contracts.game import HEIGHT, TILE, WIDTH


def draw_terrain(painter):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            road = x == 2 or y == 2
            color = (216, 202, 158) if road else ((183, 205, 153) if (x + y) % 2 else (189, 210, 159))
            position = (24 + x * TILE, 152 + y * TILE)
            pygame.draw.rect(painter.canvas, color, (*position, TILE, TILE))
            tile = painter.images.get("path" if road else "grass")
            if tile:
                painter.canvas.blit(tile, position)


def draw_decorations(painter):
    if "tree" in painter.images:
        for x, y in ((5, 5), (6, 8), (12, 4), (16, 5), (16, 11), (9, 12)):
            painter.canvas.blit(painter.images["tree"], (24 + x * TILE, 152 + y * TILE))
    if "house" in painter.images:
        for x, y in ((7, 5), (13, 9)):
            px, py = 24 + x * TILE, 152 + y * TILE
            pygame.draw.polygon(painter.canvas, (155, 73, 61), ((px - 6, py), (px + 16, py - 22), (px + 38, py)))
            painter.canvas.blit(painter.images["house"], (px, py))
