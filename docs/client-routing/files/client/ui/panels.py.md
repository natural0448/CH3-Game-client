# client/ui/panels.py

## 책임

QueryView를 읽어 메인 스레드에서 표와 카드만 그린다. 요청·상태 갱신·Spark/Kafka 호출은 없다.

## 함수

`draw_analytics(painter, slot)`

```text
opened일 때 확정 사실 통계 카드와 새로 읽기·닫기 control 표시
busy·available=false·오류 상태를 0건으로 바꾸지 않고 구분해 표시
source raw를 'DB 내보내기 스냅샷', delta를 'event_id별 고유 사실 Delta'로 표시
generated_at을 '집계 생성 시각', event_count를 '고유 확정 사실 수'로 표시
record_count가 있을 때만 '선택한 원천의 행 수' 표시
by_action과 by_room의 받은 행만 일반 텍스트 표로 표시
빈 배열은 각각 '게시할 행동 그룹 없음', '게시할 방 그룹 없음'으로 표시
온라인 인원·성공률·보상량이 아니라는 안내와 API 응답 대조 문구 표시
```

`draw_history(painter, slot)` — 개인 최근 이력의 시간, 행동, transition과 event_id를 네 행씩 그린다.

`draw_actions(painter, slot)`

```text
opened이면 조회/닫기 control과 '고정 snapshot · 마지막 집계 기준' 표시
busy·available=false·오류는 0건으로 바꾸지 않고 문구 표시
true이면 source_topic/source_kind/generated_at 표시
'고유 행동 수', '원본 전달 행 수' 구분
ACTION_TYPES 세 개 action_label/count 카드와 방별 목록 표시
접속자 수·잔액·현재 이동 횟수와 다를 수 있다는 안내 표시
방별 목록은 페이지당 세 행 표시
확정 사실 수집·뒤 시각 입력에 따른 watermark 진행·창 확정·요약 갱신 순서를 도움말로 표시
```

`draw_ingest(painter, slot)`

```text
opened이면 'Kafka 수집 통계', 다시 읽기, 닫기 control 표시
이미 게시된 결과만 읽고 Spark를 실행하지 않는다는 안내 표시
busy·available=false·401/503 오류를 숫자 0으로 바꾸지 않고 문구 표시
true이면 source/generated_at과 수집 레코드·고유 사건·재전달 레코드 카드 표시
by_action의 event_type/count를 작은 목록으로 표시
```

`draw_windows(painter, slot)`

```text
opened이면 시간 창 다시 읽기·닫기와 전체/tumbling/sliding 필터 표시
available=false이면 '아직 창 요약이 없습니다', true의 빈 배열이면 '확정된 게시 대상 창이 없습니다' 표시
true이면 generated_at과 kind/window_start/window_end/event_type/count를 최근 다섯 행으로 표시
필터 버튼과 각 행의 kind는 `tumbling`, `sliding` 원문으로 표시
시작 포함·끝 미포함과 중복 전달 가능성을 안내
필터는 QueryView.filter_value로 이미 받은 windows만 거르고 새 요청을 만들지 않음
창 행의 count를 고유 사건 수로 합산하지 않음
```

`_local_stamp(value)` — timezone이 있는 ISO 문자열을 PC 현지 시간의 초 단위 문자열로 변환한다.

`draw_load(painter, slot)`

```text
opened일 때 '최근 수업 측정'과 버튼형 GET 안내 표시
busy·available=false·오류를 실제 0으로 바꾸지 않고 '아직 측정 전'과 구분
generated_at, 설정 기간, 실제 경과, 요청/연결 성공/최고 동시 연결 표시
성공·오류·처리율 건/초·nullable RTT ms 표시
by_room에서 success_count가 가장 큰 방을 '이번 실행의 최다 응답 방'으로 표시
success_count가 같으면 room_id 오름차순에서 앞선 방 선택
by_room을 이번 연결 수와 성공 응답 수의 세로 목록으로 표시
현재 온라인 인원과 다른 이번 부하 실행 결과임을 안내
```

`draw_metrics(painter, slot)`

```text
opened일 때 '분석 전달 상태'와 저장 snapshot 조회 안내 표시
metrics.generated_at과 window_start/end를 표시
최근 확정·발행 표시·현재 미발행 표시를 서로 다른 count로 표시
Kafka topic/group과 known lag, 불완전하면 '일부 위치 미확인' 표시
Spark progress가 있으면 별도의 timestamp·batch·input 행 표시
RTT·Kafka 위치·Spark 기록은 서로 다른 단계라는 안내 표시
```

`draw_api(painter, slot, kind, scroll)` — 고정 GET path, status, 허용 JSON을 일반 텍스트로만 그리며 최대 5줄 viewport를 적용한다.

`draw_lake(painter, slot)` — painter는 메인 스레드의 Painter, slot은 lake QueryView(또는 검사에서 QuerySlot)다. 반환값은 None이며 상태를 수정하지 않는다.

```text
opened=False이면 종료
기존 panel_rect에 제목 '원본 보존', lake_refresh/lake_close 버튼 표시
busy이면 읽는 중 문구 표시하고 종료
response.json이 없으면 안전한 오류·로그인 안내 표시하고 종료
pending이면 검사 준비 중, unavailable이면 조회 불가로 표시하고 종료
ready이면 dataset_version을 줄바꿈 가능한 일반 텍스트로 표시
rows/bytes를 두 작은 카드에 실제 단위와 함께 표시
captured_at와 generated_at을 서로 다른 PC 현지 시각 라벨로 표시
matched=True이면 '마지막 로컬 사본과 일치', False이면 '원본 비교 확인 필요'
verification_scope=local-and-copied-bytes와 마지막 로컬 비교 결과라는 안내 표시
```

값은 worker의 read_lake 허용 필드 사전에서만 온다. 직접 호출은 Painter.card/text/wrapped/button, pygame.Rect, `_local_stamp`다. HTTP·파일 복사·Spark·게임 상태 쓰기를 수행하지 않는다. 준비·오류 상태에서는 0행/0bytes를 만들지 않는다.

`draw_query_panels(painter, queries)` — analytics/history/actions/ingest/windows/load/metrics/lake 순서로 위 draw 함수를 호출한다.

직접 호출: `Painter`, `pygame.draw.line`, `json.dumps`, `datetime.fromisoformat`, `QUERY_SPECS`.
