"""Decode public PNG bytes on the main thread and draw both reserved ad positions."""
import io
import threading

import pygame

from client.ui.drawing import GREEN, INK, MUTED


class AdsRenderer:
    def __init__(self):
        self.images = {}
        self.failures = {}

    def image(self, slot):
        assert threading.current_thread() is threading.main_thread()
        if not slot.decision["creative_path"]:
            self.images.pop(slot.slot_id, None)
            return None
        cached = self.images.get(slot.slot_id)
        decision_id = slot.decision["decision_id"]
        if cached and cached[0] == decision_id:
            return cached[1]
        if not slot.image_bytes:
            raise ValueError("missing_image")
        image = pygame.image.load(io.BytesIO(slot.image_bytes)).convert_alpha()
        self.images[slot.slot_id] = (decision_id, image)
        return image

    def draw(self, painter, ads, authenticated):
        receipts = {}
        self.failures = {}
        if not authenticated:
            self.images.clear()
        for name, slot in ads.items():
            village = name == "village-board"
            rect = painter.layout.ad_cards[name]
            color = (231, 240, 216)
            if slot.decision and "camp-tea" in slot.decision["creative_path"]:
                color = (245, 232, 208)
            painter.card(rect, color)
            painter.button("ad_village_refresh" if village else "ad_lobby_refresh",
                           "새로 보기" if village else "새로", authenticated and slot.can_request)
            if village:
                painter.text("마을 게시판 · AD", (rect.x + 16, rect.y + 12), 13, GREEN)
            if not authenticated or slot.status != "ready":
                painter.wrapped(slot.message if authenticated else "게임 로그인 후 광고를 받습니다.",
                                pygame.Rect(rect.x + 16, rect.y + (55 if village else 8),
                                            rect.width - (32 if village else 65), 45 if village else 20),
                                13, MUTED)
                continue
            try:
                image = self.image(slot)
            except (pygame.error, OSError, ValueError):
                self.failures[name] = slot.decision["decision_id"]
                painter.text("이미지 표시 실패 · 다시 요청하세요.",
                             (rect.x + 16, rect.y + (55 if village else 10)), 13, MUTED)
                continue
            decision = slot.decision
            if image:
                size = 64 if village else 32
                painter.canvas.blit(pygame.transform.scale(image, (size, size)),
                                    (rect.x + (16 if village else 8), rect.y + (47 if village else 5)))
            if village:
                text_x = rect.x + (96 if image else 16)
                painter.wrapped(decision["title"], pygame.Rect(text_x, rect.y + 44, rect.right - text_x - 12, 27), 20, INK)
                painter.wrapped(decision["body"], pygame.Rect(text_x, rect.y + 72, rect.right - text_x - 12, 23), 13, MUTED)
                painter.text(f"{decision['bid_amount']} 포인트", (text_x, rect.y + 98), 15, GREEN)
                progress = f"노출 {'완료' if slot.impression_ok else '대기'} · 클릭 {'완료' if slot.click_ok else '대기'}"
                status = ("광고 새 요청 필요" if slot.event_rejected else
                          "실적 저장 실패 · 재시도 대기" if slot.event_error else progress)
                painter.text(status,
                             (rect.x + 16, rect.y + 122), 13, MUTED)
                painter.wrapped("ID " + decision["decision_id"],
                                pygame.Rect(rect.x + 16, rect.y + 143, rect.width - 32, 20), 13, MUTED)
            else:
                painter.wrapped(f"{decision['title']} · {decision['bid_amount']}p",
                                pygame.Rect(rect.x + 46, rect.y + 2, rect.width - 110, 19), 13, INK)
                painter.text(decision["decision_id"], (rect.x + 46, rect.y + 21), 13, MUTED)
            receipts[name] = decision["decision_id"]
        return receipts
