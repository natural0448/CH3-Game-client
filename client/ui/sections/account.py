"""Login and logout controls."""
import pygame

from client.ui.drawing import GREEN, INK, MUTED


def draw_account(painter, app):
    draft = app.login
    for name, value, placeholder in (
        ("username", draft.username, "아이디"),
        ("password", "•" * draft.password_length, "비밀번호"),
    ):
        rect = painter.layout.controls[name]
        painter.card(rect)
        if name == draft.focus:
            pygame.draw.rect(painter.canvas, GREEN, rect, 2, border_radius=8)
        clip = painter.canvas.get_clip()
        painter.canvas.set_clip(rect.inflate(-18, -6))
        painter.text(value or placeholder, (rect.x + 12, rect.y + 9), 17, INK if value else MUTED)
        painter.canvas.set_clip(clip)
    painter.button("login", "마을 입장", app.phase == "signed_out" and not app.closing)
    painter.text("방향키 이동 · Space 채집 · X 수련", (756, 108), 15, MUTED)
