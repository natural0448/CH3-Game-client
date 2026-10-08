# client/contracts/ads.py

## 23일차 1~2교시 최종 반영

SLOTS=frozenset(village-board,lobby-banner), CREATIVE_PATHS=frozenset(blank,forest-tools PNG,camp-tea PNG). read_decision은 dict/슬롯일치/정수1..10000/제목80·본문300/공개 문자열을 검사한다. None 광고를 허용하고 bid_units를 bid_amount로 정규화한다. 선택 public allowlist만 새 dict에 복사한다. EVENT_TYPES=frozenset(impression,click). read_ad_event는 해당 decision_id:event_type 문자열, 종류 일치, created의 정확한 bool 타입을 검사하고 세 필드만 반환한다.

### `read_ad_event(data, decision_id, event_type)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| data | 없음 | 요청/조회 public dict 또는 Django POST mapping; 파일 책임의 필드·타입 범위 참조. |
| decision_id | 없음 | 현재 선택된 결정의 비어 있지 않은 문자열 ID; 저장된 subject와 일치해야 한다. |
| event_type | 없음 | impression 또는 click 문자열. click은 저장/확인된 impression이 선행해야 한다. |

반환·실패: allowlist dict 또는 ValueError.

의사코드: dict/결정:종류 일치 → event_type 일치 → created bool → 세필드 반환.

직접 호출: `ValueError`, `isinstance`, `data.get`, `type`. 기대 결과는 위 반환·상태 변화에 사용한다. 하위 계층 내부 구현은 그 짝 문서를 따른다.

### `read_decision(data, slot_id)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| data | 없음 | 요청/조회 public dict 또는 Django POST mapping; 파일 책임의 필드·타입 범위 참조. |
| slot_id | 없음 | village-board 또는 lobby-banner. |

반환·실패: public dict 또는 None; 잘못된 선택 ValueError.

의사코드: dict/슬롯 → empty 판단 → 금액/PNG path/공개 문자열 검사 → allowlist dict 반환.

직접 호출: `data.get`, `any`, `ValueError`, `isinstance`, `type`, `len`, `result.values`. 기대 결과는 위 반환·상태 변화에 사용한다. 하위 계층 내부 구현은 그 짝 문서를 따른다.
