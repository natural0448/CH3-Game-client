# tests/test_actions_contract.py

## 책임

행동 통계 allowlist와 available 의미를 검사한다.

## 메서드

`ActionContractTests.test_allowlist_keeps_source_unchanged(self)` — 비밀 필드 제외와 입력 불변을 검사한다.

`ActionContractTests.test_unavailable_is_not_measured_zero(self)` — 미생성 false와 실제 0 측정값을 구분한다.

`ActionContractTests.test_wrong_source_and_duplicate_action_are_rejected(self)` — live source와 중복 행동을 거절하는지 검사한다.

직접 호출: `read_actions`, `copy.deepcopy`, `action_snapshot`.
