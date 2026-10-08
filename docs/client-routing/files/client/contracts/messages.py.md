# client/contracts/messages.py

기존 NetworkRequest/NetworkEvent는 dict[str,Any] TypeAlias다. 이벤트는 kind=ad_event/ad_event_error, slot_id/player_id/request_id/decision_id/event_type, status, 공개 ad_event receipt 또는 message, needs_login과event_rejected를 전달한다. 매체 키·쿠키·CSRF 토큰·로그인 비밀값은 결과에 넣지 않는다. dataclass/별도 교안 ports를 복제하지 않고 기존 계약을 유지한다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.
