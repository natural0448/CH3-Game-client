"""Connection and bottom message overlays."""
import pygame

from client.ui.drawing import GREEN


def draw_connection_overlay(painter, game):
    if not game.ready:
        overlay = pygame.Surface((640, 480), pygame.SRCALPHA)
        overlay.fill((244, 245, 232, 140))
        painter.canvas.blit(overlay, (24, 152))
        painter.card(pygame.Rect(144, 348, 400, 72))
        painter.text("서버의 확정 상태를 기다리고 있어요", (180, 371), 20)


def draw_status(painter, app, asset_notice):
    painter.wrapped("연결을 정리하는 중…" if app.closing else (asset_notice or app.message),
                    pygame.Rect(24, 820, 1048, 43), 15, GREEN)
