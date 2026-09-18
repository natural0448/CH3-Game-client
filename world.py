"""Draw confirmed room state and preserved CC0 art, main thread only."""
import pygame
from state import GATHER_TILE, TRAIN_TILE, WIDTH, HEIGHT, TILE

GREEN = (29, 105, 83)
INK = (33, 53, 49)
WHITE = (255, 254, 247)


def draw_world(renderer, state):
    renderer.card(pygame.Rect(22, 150, 644, 484))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = (183, 205, 153) if (x + y) % 2 else (189, 210, 159)
            if x == 2 or y == 2:
                color = (216, 202, 158)
            pygame.draw.rect(renderer.canvas, color, (24 + x * TILE, 152 + y * TILE, TILE, TILE))
            tile = renderer.images.get("path" if x == 2 or y == 2 else "grass")
            if tile:
                renderer.canvas.blit(tile, (24 + x * TILE, 152 + y * TILE))
    # Decorations only: no client-side walls, collision, or reward rules.
    if "tree" in renderer.images:
        for x, y in ((5, 5), (6, 8), (12, 4), (16, 5), (16, 11), (9, 12)):
            renderer.canvas.blit(renderer.images["tree"], (24 + x * TILE, 152 + y * TILE))
    if "house" in renderer.images:
        for x, y in ((7, 5), (13, 9)):
            px, py = 24 + x * TILE, 152 + y * TILE
            pygame.draw.polygon(renderer.canvas, (155, 73, 61), ((px - 6, py), (px + 16, py - 22), (px + 38, py)))
            renderer.canvas.blit(renderer.images["house"], (px, py))
    gx, gy = (24 + GATHER_TILE[0] * TILE, 152 + GATHER_TILE[1] * TILE)
    pygame.draw.rect(renderer.canvas, (237, 193, 76), (gx + 2, gy + 2, 28, 28), border_radius=6)
    pygame.draw.circle(renderer.canvas, (105, 125, 44), (gx + 16, gy + 17), 9)
    pygame.draw.circle(renderer.canvas, (247, 224, 124), (gx + 16, gy + 12), 5)
    renderer.text("채집 (2, 2)", (gx - 12, gy + 34), 13)
    tx, ty = 24 + TRAIN_TILE[0] * TILE, 152 + TRAIN_TILE[1] * TILE
    pygame.draw.rect(renderer.canvas, (166, 191, 221), (tx + 2, ty + 2, 28, 28), border_radius=6)
    pygame.draw.line(renderer.canvas, (63, 82, 132), (tx + 16, ty + 25), (tx + 16, ty + 6), 3)
    pygame.draw.polygon(renderer.canvas, (63, 82, 132), [(tx + 16, ty + 5), (tx + 28, ty + 9), (tx + 16, ty + 14)])
    renderer.text("개인 수련 (3, 2)", (tx + 36, ty + 4), 13)
    if state.own is not None and state.has_ws_state:
        occupants = {}
        for player in sorted(state.players.values(), key=lambda p: (p["y"], p["player_id"] == state.own["player_id"], p["player_id"])):
            occupants.setdefault((player["x"], player["y"]), []).append(player["player_id"])
            x, y = 24 + player["x"] * TILE, 152 + player["y"] * TILE
            mine = player["player_id"] == state.own["player_id"]
            pygame.draw.ellipse(renderer.canvas, (128, 153, 112), (x + 4, y + 23, 25, 7))
            if "hero" in renderer.images:
                hero = renderer.images["hero"]
                renderer.canvas.blit(hero, hero.get_rect(midbottom=(x + TILE // 2, y + TILE)))
            else:
                pygame.draw.rect(renderer.canvas, GREEN, (x + 7, y + 12, 18, 16), border_radius=5)
                pygame.draw.circle(renderer.canvas, (255, 227, 185), (x + 16, y + 9), 7)
                pygame.draw.circle(renderer.canvas, INK, (x + 19, y + 9), 1)
            pygame.draw.rect(renderer.canvas, GREEN if mine else (78, 95, 171), (x + 1, y + 1, 30, 30), 2, border_radius=5)
        for (tile_x, tile_y), ids in occupants.items():
            # Reuse tile occupants so overlapping players share a nameplate.
            label = ", ".join(state.players[pid].get("username") or f"#{pid}" for pid in ids[:3])
            if len(ids) > 3:
                label += f" +{len(ids) - 3}"
            if len(ids) > 1:
                label += f" ({len(ids)}명)"
            text = renderer.fonts[13].render(label, True, INK)
            # The top row has a narrow gap below the login controls.
            max_height = 11 if tile_y == 0 else text.get_height()
            scale = min(1, 636 / max(1, text.get_width()), max_height / text.get_height())
            if scale < 1:
                text = pygame.transform.smoothscale(text, (max(1, int(text.get_width() * scale)), max(1, int(text.get_height() * scale))))
            rect = text.get_rect(midbottom=(24 + tile_x * TILE + TILE // 2, 152 + tile_y * TILE - 3))
            rect.x = max(26, min(rect.x, 662 - rect.width))
            pygame.draw.rect(renderer.canvas, WHITE, rect.inflate(4, 2), border_radius=3)
            renderer.canvas.blit(text, rect)
    if not state.ready:
        overlay = pygame.Surface((640, 480), pygame.SRCALPHA)
        overlay.fill((244, 245, 232, 140))
        renderer.canvas.blit(overlay, (24, 152))
        renderer.card(pygame.Rect(144, 348, 400, 72))
        renderer.text("서버의 확정 상태를 기다리고 있어요", (180, 371), 20)

