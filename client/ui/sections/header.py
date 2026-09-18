"""Title and connection summary."""
import pygame

from client.ui.drawing import GREEN, MUTED

PHASES = {
    "signed_out": "로그인 전", "authenticating": "로그인 확인 중",
    "connecting": "첫 상태 대기", "connected": "마을 연결됨",
    "disconnected": "연결 끊김", "reconnecting": "재연결 중",
    "logging_out": "로그아웃 중", "stopped": "종료됨",
}


def draw_header(painter, app, game, fps):
    painter.text("작은 마을", (24, 19), 32)
    own = game.own or {}
    summary = (f"{own.get('room_id', '방 —')}  |  {game.online_label}  |  "
               f"내 위치 ({own.get('x', '—')}, {own.get('y', '—')}) · 동전 {own.get('coins', '—')}  |  "
               f"{PHASES.get(app.phase, app.phase)}")
    image = painter.fonts[15].render(summary, True, GREEN if game.ready else MUTED)
    if image.get_width() > 905:
        ratio = 905 / image.get_width()
        image = pygame.transform.smoothscale(image, (905, max(1, int(image.get_height() * ratio))))
    painter.canvas.blit(image, (26, 63))
    painter.text(f"네트워크 · {PHASES.get(app.phase, app.phase)}", (690, 26), 17,
                 GREEN if game.ready else MUTED)
    painter.text(f"화면 FPS  {fps:.0f}", (954, 62), 15, MUTED)
