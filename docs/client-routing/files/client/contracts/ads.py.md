# client/contracts/ads.py

## 22일차 이미지 광고 최종 반영

SLOTS=frozenset(village-board,lobby-banner), CREATIVE_PATHS=frozenset(blank,forest-tools PNG,camp-tea PNG). read_decision은 dict/슬롯일치/정수1..10000/제목80·본문300/공개 문자열을 검사한다. None 광고를 허용하고 bid_units를 bid_amount로 정규화한다. 선택 public allowlist만 새 dict에 복사한다.

### `read_decision(data, slot_id)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| data | 없음 | 요청/조회 public dict 또는 Django POST mapping; 파일 책임의 필드·타입 범위 참조. |
| slot_id | 없음 | village-board 또는 lobby-banner. |

반환·실패: public dict 또는 None; 잘못된 선택 ValueError.

의사코드: dict/슬롯 → empty 판단 → 금액/PNG path/공개 문자열 검사 → allowlist dict 반환.

직접 호출: `data.get`, `any`, `ValueError`, `isinstance`, `type`, `len`, `result.values`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
