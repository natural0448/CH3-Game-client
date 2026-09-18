"""Confirmed player state and game command buttons."""
import pygame

from client.contracts.game import TRAIN_TILE


def draw_commands(painter, app, game):
    painter.card(pygame.Rect(688, 152, 388, 132))
    painter.text("나의 확정 상태", (710, 168), 20)
    own = game.own or {}
    painter.text(f"player_id  {own.get('player_id', '—')}", (710, 202), 15)
    painter.text(f"room_id  {own.get('room_id', '—')}", (710, 224), 15)
    painter.text(
        f"x  {own.get('x', '—')}   y  {own.get('y', '—')}     coins  {own.get('coins', '—')}     version  {own.get('version', '—')}",
        (710, 251), 15,
    )
    painter.card(pygame.Rect(688, 296, 388, 178))
    enabled = game.ready and game.pending is None and not app.closing
    for name, label in (("up", "위"), ("left", "왼쪽"), ("down", "아래"), ("right", "오른쪽")):
        painter.button(name, label, enabled)
    painter.button("gather", "채집 · (2, 2)", enabled)
    painter.button("train", "수련 [X] · (3, 2)",
                   enabled and (own.get("x"), own.get("y")) == TRAIN_TILE)
