# client/ui/world/nameplates.py

## 책임

모든 actor가 그려진 뒤 캐릭터 상단에 player label을 그린다.

## 함수

`draw_nameplates(painter, nameplates)` — font render, top row 높이와 world 폭에 맞춘 scale/clamp, 흰 배경과 text를 그린다.

직접 호출: font, `pygame.transform.smoothscale`, `pygame.draw.rect`, Surface.blit.
