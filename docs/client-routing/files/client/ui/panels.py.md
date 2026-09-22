# client/ui/panels.py

## 책임

QueryView를 읽어 메인 스레드에서 표와 카드만 그린다. 요청·상태 갱신·Spark/Kafka 호출은 없다.

## 함수

`draw_analytics(painter, slot)` — available 집계의 전체 사실 수, 행동/방 표와 페이지 또는 미생성 문구를 그린다.

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

`draw_api(painter, slot, kind, scroll)` — 고정 GET path, status, 허용 JSON을 일반 텍스트로만 그리며 최대 5줄 viewport를 적용한다.

`draw_query_panels(painter, queries)` — analytics/history/actions/ingest/windows 순서로 위 draw 함수를 호출한다.

직접 호출: `Painter`, `pygame.draw.line`, `json.dumps`, `datetime.fromisoformat`, `QUERY_SPECS`.
