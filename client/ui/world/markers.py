"""Gather and training markers; rewards remain server-owned."""
import pygame

from client.contracts.game import GATHER_TILE, TILE, TRAIN_TILE


def draw_markers(painter):
    gx, gy = 24 + GATHER_TILE[0] * TILE, 152 + GATHER_TILE[1] * TILE
    pygame.draw.rect(painter.canvas, (237, 193, 76), (gx + 2, gy + 2, 28, 28), border_radius=6)
    pygame.draw.circle(painter.canvas, (105, 125, 44), (gx + 16, gy + 17), 9)
    pygame.draw.circle(painter.canvas, (247, 224, 124), (gx + 16, gy + 12), 5)
    painter.text("채집 (2, 2)", (gx - 12, gy + 34), 13)
    tx, ty = 24 + TRAIN_TILE[0] * TILE, 152 + TRAIN_TILE[1] * TILE
    pygame.draw.rect(painter.canvas, (166, 191, 221), (tx + 2, ty + 2, 28, 28), border_radius=6)
    pygame.draw.line(painter.canvas, (63, 82, 132), (tx + 16, ty + 25), (tx + 16, ty + 6), 3)
    pygame.draw.polygon(painter.canvas, (63, 82, 132), [(tx + 16, ty + 5), (tx + 28, ty + 9), (tx + 16, ty + 14)])
    painter.text("개인 수련 (3, 2)", (tx + 36, ty + 4), 13)
