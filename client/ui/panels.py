"""Stateless read-only query panels."""
import json
from datetime import datetime

import pygame

from client.contracts.queries import ACTION_TYPES, QUERY_SPECS
from client.ui.drawing import INK, LINE, MUTED


def draw_analytics(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("확정 사실 통계", (56, 179), 20)
    painter.button("analytics_refresh", "조회 중…" if slot.busy else "새로 읽기", not slot.busy)
    painter.button("analytics_close", "닫기")
    painter.text("게시된 집계 결과 · 버튼 한 번에 GET 한 번", (56, 213), 13)
    if slot.busy:
        painter.text("통계를 읽고 있어요…", (72, 317), 20)
        return
    response = slot.response or {}
    data = response.get("json")
    if data is None:
        painter.wrapped(response.get("message", "새로 읽기 버튼을 눌러 주세요."), pygame.Rect(72, 303, 544, 120), 20)
        return
    if not data.get("available"):
        painter.wrapped("아직 집계가 없습니다", pygame.Rect(72, 303, 544, 120), 20)
        return
    source_label = {
        "raw": "DB 내보내기 스냅샷",
        "delta": "event_id별 고유 사실 Delta",
    }[data["source"]]
    painter.text("원천: " + source_label, (56, 242), 13)
    stamp = datetime.fromisoformat(data["generated_at"]).astimezone().isoformat(
        sep=" ", timespec="seconds"
    )
    painter.text("집계 생성 시각: " + stamp, (56, 264), 13)
    painter.text(f"고유 확정 사실 수  {data['event_count']:,}건", (56, 294), 26)
    if "record_count" in data:
        painter.text(f"선택한 원천의 행 수  {data['record_count']:,}행", (352, 300), 15)
    painter.text("행동별", (56, 334), 17)
    painter.text("방별", (352, 334), 17)
    for field, key, left in (("by_action", "event_type", 56), ("by_room", "room_id", 352)):
        rows = data[field][slot.page * 6:(slot.page + 1) * 6]
        if not rows:
            empty = "게시할 행동 그룹 없음" if field == "by_action" else "게시할 방 그룹 없음"
            painter.text(empty, (left, 373), 15)
        for index, row in enumerate(rows):
            y = 370 + index * 33
            pygame.draw.line(painter.canvas, LINE, (left, y + 29), (left + 264, y + 29))
            old_clip = painter.canvas.get_clip()
            painter.canvas.set_clip(pygame.Rect(left, y, 197, 28))
            painter.text(row[key], (left, y), 15)
            painter.canvas.set_clip(old_clip)
            count = painter.fonts[15].render(str(row["count"]), True, INK)
            painter.canvas.blit(count, count.get_rect(topright=(left + 264, y)))
    count = max(len(data["by_action"]), len(data["by_room"]))
    pages = max(1, (count + 5) // 6)
    painter.text("온라인 인원·성공률·보상량이 아닙니다", (56, 565), 13)
    painter.text(f"목록 {slot.page + 1}/{pages} · API 응답 보기와 대조", (56, 590), 13)
    painter.button("analytics_previous", "이전", slot.page > 0)
    painter.button("analytics_next", "다음", slot.page + 1 < pages)


def draw_history(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("내 행동 이력", (56, 179), 20)
    painter.button("history_close", "닫기")
    painter.text("내 최근 20개 · 버튼으로만 조회 · 전체 집계 아님", (56, 213), 13)
    response = slot.response or {}
    rows = (response.get("json") or {}).get("events", [])
    if slot.busy or not rows:
        painter.wrapped("이력을 읽고 있어요…" if slot.busy else response.get("message", "내 이력 읽기를 눌러 주세요."),
                        pygame.Rect(56, 288, 556, 140), 20)
        return
    for index, event in enumerate(rows[slot.page * 4:(slot.page + 1) * 4]):
        y = 248 + index * 78
        stamp = datetime.fromisoformat(event["event_time"]).astimezone().strftime("%m-%d %H:%M:%S")
        painter.text(f"{stamp}   {event['event_type']}", (56, y), 15)
        transition = event["payload"].get("transition")
        label = ("확장 이전 기록 · step/reward — · action 기록 없음" if transition is None else
                 f"step {transition['step']}  ·  reward {transition['reward']}  ·  action {transition['action']['type']}")
        painter.text(label, (56, y + 23), 13)
        painter.text("event_id: " + event["event_id"], (56, y + 43), 13, MUTED)
        pygame.draw.line(painter.canvas, LINE, (56, y + 71), (630, y + 71))
    pages = max(1, (len(rows) + 3) // 4)
    painter.text(f"{slot.page + 1}/{pages} 페이지 · 시각은 PC 현지 시간", (56, 591), 13)
    painter.button("history_previous", "이전", slot.page > 0)
    painter.button("history_next", "다음", slot.page + 1 < pages)


def draw_actions(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("행동 통계", (56, 177), 20)
    painter.button("actions_refresh", "조회 중…" if slot.busy else "다시 조회", not slot.busy)
    painter.button("actions_close", "닫기")
    painter.text("고정 snapshot · 마지막 집계 기준", (56, 215), 15)
    data = (slot.response or {}).get("json")
    if slot.busy or data is None or not data.get("available"):
        if slot.busy:
            message = "행동 통계를 읽고 있어요…"
        elif data is not None and data.get("available") is False:
            message = "행동 집계가 아직 없습니다"
        else:
            message = (slot.response or {}).get("message", "조회 버튼을 눌러 주세요.")
        painter.wrapped(message, pygame.Rect(56, 296, 556, 140), 20)
        return
    summary = data["summary"]
    painter.text("source_topic: " + data["source_topic"], (56, 243), 13)
    painter.text("source_kind: " + data["source_kind"], (56, 264), 13)
    stamp = datetime.fromisoformat(summary["generated_at"]).astimezone().isoformat(sep=" ", timespec="seconds")
    painter.text("집계 생성 시각: " + stamp, (56, 285), 13)
    painter.wrapped(f"고유 행동 수  {summary['event_count']:,}건", pygame.Rect(56, 312, 290, 36), 20)
    painter.wrapped(f"원본 전달 행 수  {data['raw_record_count']:,}행", pygame.Rect(354, 316, 276, 32), 15)
    by_type = {row["event_type"]: row for row in summary["by_action"]}
    for index, event_type in enumerate(ACTION_TYPES):
        left = 56 + index * 194
        rect = pygame.Rect(left, 353, 184, 73)
        painter.card(rect, (235, 241, 229))
        row = by_type.get(event_type)
        painter.wrapped(row["action_label"] if row else "해당 행동 항목 없음", pygame.Rect(left + 10, 360, 164, 23), 15)
        painter.wrapped(f"{row['count']:,}건" if row else "—", pygame.Rect(left + 10, 389, 164, 28), 20)
    painter.text("방별 행동 수", (56, 437), 15)
    rows = summary["by_room"]
    if not rows:
        painter.text("표시할 방 항목 없음", (56, 463), 13)
    for index, row in enumerate(rows[slot.page * 3:(slot.page + 1) * 3]):
        y = 461 + index * 23
        painter.wrapped(row["room_id"], pygame.Rect(56, y, 420, 23), 13)
        painter.wrapped(f"{row['count']:,}건", pygame.Rect(500, y, 130, 23), 13)
    painter.text("접속자 수·잔액이 아니며, 현재 화면의 이동 횟수와 다를 수 있습니다.", (56, 534), 13)
    painter.wrapped(
        "확정 사실은 먼저 수집됩니다. 뒤 시각의 레코드로 watermark가 진행된 뒤 창이 확정됩니다. "
        "창 요약을 갱신한 다음 통계를 조회하세요.",
        pygame.Rect(56, 553, 574, 34),
        13,
    )
    pages = max(1, (len(rows) + 2) // 3)
    painter.text(f"방 목록 {slot.page + 1}/{pages}", (56, 592), 13)
    painter.button("actions_previous", "이전", slot.page > 0)
    painter.button("actions_next", "다음", slot.page + 1 < pages)


def draw_ingest(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("Kafka 수집 통계", (56, 177), 20)
    painter.button("ingest_refresh", "조회 중…" if slot.busy else "통계 다시 읽기", not slot.busy)
    painter.button("ingest_close", "닫기")
    painter.text("이미 게시된 결과만 읽습니다 · Spark 실행 안 함", (56, 215), 15)
    response = slot.response or {}
    data = response.get("json")
    if slot.busy or data is None or not data.get("available"):
        if slot.busy:
            message = "Kafka 수집 통계를 읽고 있어요…"
        elif data is not None and data.get("available") is False:
            message = "아직 Kafka 수집 통계가 준비되지 않았어요. 수집과 집계를 마친 뒤 다시 읽어 주세요."
        else:
            message = response.get("message", "통계 다시 읽기 버튼을 눌러 주세요.")
        painter.wrapped(message, pygame.Rect(56, 296, 556, 140), 20)
        return
    painter.text("source: " + data["source"], (56, 247), 13)
    stamp = datetime.fromisoformat(data["generated_at"]).astimezone().isoformat(
        sep=" ", timespec="seconds"
    )
    painter.text("집계 생성 시각: " + stamp, (56, 270), 13)
    cards = (
        ("수집 레코드", data["record_count"]),
        ("고유 사건", data["event_count"]),
        ("재전달 레코드", data["duplicate_record_count"]),
    )
    for index, (label, value) in enumerate(cards):
        left = 56 + index * 194
        rect = pygame.Rect(left, 303, 184, 78)
        painter.card(rect, (235, 241, 229))
        painter.text(label, (left + 10, 314), 15)
        painter.text(f"{value:,}", (left + 10, 340), 26)
    painter.text("행동별 수집 사건", (56, 407), 17)
    if not data["by_action"]:
        painter.text("표시할 행동 항목 없음", (56, 442), 15)
    for index, row in enumerate(data["by_action"]):
        y = 438 + index * 37
        pygame.draw.line(painter.canvas, LINE, (56, y + 29), (630, y + 29))
        painter.text(row["event_type"], (56, y), 15)
        count = painter.fonts[15].render(f"{row['count']:,}건", True, INK)
        painter.canvas.blit(count, count.get_rect(topright=(630, y)))
    painter.text("수집 레코드와 고유 사건은 접속자 수나 현재 이동 횟수가 아닙니다.", (56, 574), 13)


def draw_windows(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("확정 시간 창", (56, 177), 20)
    painter.button("windows_refresh", "조회 중…" if slot.busy else "시간 창 다시 읽기", not slot.busy)
    painter.button("windows_close", "닫기")
    painter.wrapped(
        "확정 시간 창의 전달 레코드 수(중복 전달 포함 가능)",
        pygame.Rect(56, 214, 560, 38),
        15,
    )
    painter.text("시작 시각 포함 · 끝 시각 미포함", (56, 239), 13, MUTED)
    labels = {
        "all": "전체",
        "tumbling": "tumbling",
        "sliding": "sliding",
    }
    for value, label in labels.items():
        selected = "✓ " if slot.filter_value == value else ""
        painter.button("windows_filter_" + value, selected + label)

    response = slot.response or {}
    data = response.get("json")
    if slot.busy or data is None or not data.get("available"):
        if slot.busy:
            message = "시간 창 요약을 읽고 있어요…"
        elif data is not None and data.get("available") is False:
            message = "아직 창 요약이 없습니다"
        else:
            message = response.get("message", "시간 창 버튼을 눌러 주세요.")
        painter.wrapped(message, pygame.Rect(56, 329, 556, 120), 20)
        return

    stamp = datetime.fromisoformat(data["generated_at"]).astimezone().isoformat(
        sep=" ", timespec="seconds"
    )
    painter.text("요약 생성 시각: " + stamp, (56, 301), 13)
    rows = data["windows"]
    if slot.filter_value != "all":
        rows = [row for row in rows if row["kind"] == slot.filter_value]
    rows = sorted(rows, key=lambda row: (row["window_start"], row["event_type"]), reverse=True)[:5]
    if not rows:
        painter.wrapped("확정된 게시 대상 창이 없습니다", pygame.Rect(56, 350, 556, 80), 20)
        return

    painter.text("종류 · 행동 · 전달 레코드", (56, 329), 13, MUTED)
    for index, row in enumerate(rows):
        y = 354 + index * 45
        painter.text(f"{row['kind']} · {row['event_type']}", (56, y), 15)
        count = painter.fonts[15].render(f"{row['count']:,}건", True, INK)
        painter.canvas.blit(count, count.get_rect(topright=(630, y)))
        start = datetime.fromisoformat(row["window_start"]).astimezone().strftime("%m-%d %H:%M:%S")
        end = datetime.fromisoformat(row["window_end"]).astimezone().strftime("%m-%d %H:%M:%S")
        painter.text(f"{start} ≤ event_time < {end}", (72, y + 21), 13, MUTED)
        pygame.draw.line(painter.canvas, LINE, (56, y + 40), (630, y + 40))
    painter.text("최근 5행 · 필터는 받은 결과에만 적용 · 합계는 고유 사건 수가 아닙니다.", (56, 590), 13)


def _local_stamp(value):
    return datetime.fromisoformat(value).astimezone().isoformat(
        sep=" ", timespec="seconds"
    )


def draw_load(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("최근 수업 측정", (56, 177), 20)
    painter.button("load_refresh", "조회 중…" if slot.busy else "측정 다시 읽기", not slot.busy)
    painter.button("load_close", "닫기")
    painter.text("저장된 run-50 결과 조회 · 부하 측정을 시작하지 않음", (56, 215), 15)
    data = (slot.response or {}).get("json")
    if slot.busy or data is None or not data.get("available"):
        message = (
            "측정 결과를 읽고 있어요…" if slot.busy
            else "아직 측정 전" if data is not None
            else (slot.response or {}).get("message", "조회 버튼을 눌러 주세요.")
        )
        painter.wrapped(message, pygame.Rect(56, 296, 556, 120), 20)
        return
    report = data["load"]
    profile = report["profile"]
    painter.text("측정 생성 시각: " + _local_stamp(report["generated_at"]), (56, 243), 13)
    painter.text(
        f"설정 {profile['seconds']:g}초 / 관찰 {report['elapsed_seconds']:.3f}초 · "
        f"간격 {profile['interval_seconds']:g}초",
        (56, 266), 13,
    )
    painter.text(
        f"요청 {profile['clients']}개 · 연결 성공 {report['connected_success']}개 · "
        f"최고 동시 연결 {report['connected_peak']}개",
        (56, 300), 17,
    )
    rtt = "표본 없음" if report["rtt_p95_ms"] is None else f"{report['rtt_p95_ms']:.3f}ms"
    painter.text(
        f"성공 {report['success_count']}건 · 오류 {report['error_count']}건 · "
        f"처리율 {report['success_per_second']:.3f}건/초 · RTT p95 {rtt}",
        (56, 331), 15,
    )
    rooms = report["by_room"]
    if rooms:
        top_room = min(rooms, key=lambda row: (-row["success_count"], row["room_id"]))
        painter.text(
            f"이번 실행의 최다 응답 방: {top_room['room_id']} · "
            f"{top_room['success_count']}건",
            (56, 369), 15,
        )
    painter.text("방별 이번 부하 실행 결과", (56, 400), 17)
    painter.text("방 · 이번 연결 수 · 성공 응답 수", (56, 427), 13, MUTED)
    for index, row in enumerate(rooms[:5]):
        y = 454 + index * 27
        painter.text(
            f"{row['room_id']} · {row['connected']}개 · {row['success_count']}건",
            (72, y), 15,
        )
    painter.text("이 표는 이번 부하 실행의 결과입니다. 현재 온라인 인원이 아닙니다.", (56, 590), 13)


def draw_metrics(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("분석 전달 상태", (56, 177), 20)
    painter.button("metrics_refresh", "조회 중…" if slot.busy else "상태 다시 읽기", not slot.busy)
    painter.button("metrics_close", "닫기")
    painter.text("저장된 운영 snapshot 조회 · Kafka/Spark 작업을 시작하지 않음", (56, 215), 15)
    data = (slot.response or {}).get("json")
    if slot.busy or data is None or not data.get("available"):
        message = (
            "운영 지표를 읽고 있어요…" if slot.busy
            else "아직 측정 전" if data is not None
            else (slot.response or {}).get("message", "조회 버튼을 눌러 주세요.")
        )
        painter.wrapped(message, pygame.Rect(56, 296, 556, 120), 20)
        return
    report = data["metrics"]
    painter.text("지표 생성 시각: " + _local_stamp(report["generated_at"]), (56, 243), 13)
    painter.text(
        f"관찰 구간: {_local_stamp(report['window_start'])} ~ "
        f"{_local_stamp(report['window_end'])} ({report['window_seconds']}초)",
        (56, 266), 13,
    )
    painter.text(
        f"최근 확정 {report['confirmed_count']}건 · 최근 발행 표시 {report['published_recent']}건",
        (56, 304), 17,
    )
    oldest = report["oldest_pending_age_seconds"]
    age = "없음" if oldest is None else f"{oldest:.1f}초"
    painter.text(
        f"현재 미발행 표시 {report['pending_mark_count']}건 · 가장 오래된 표시 {age}",
        (56, 334), 15,
    )
    kafka = report["kafka"]
    suffix = "" if kafka["lag_complete"] else " · 일부 위치 미확인"
    painter.text("Python 행동 변환기 Kafka 위치", (56, 378), 17)
    painter.text(f"{kafka['topic']} · {kafka['group_id']}", (56, 406), 13)
    painter.text(f"확인 가능한 lag 합 {kafka['known_lag_sum']}건{suffix}", (56, 432), 15)
    progress = report["spark_progress"]
    painter.text("Spark 진행 기록", (56, 478), 17)
    if progress is None:
        painter.text("아직 완료된 Spark batch 기록이 없습니다", (56, 506), 15)
    else:
        painter.text("Spark 기록 시각: " + _local_stamp(progress["timestamp"]), (56, 506), 13)
        painter.text(
            f"{progress['name']} · batch {progress['batchId']} · 입력 {progress['numInputRows']}행",
            (56, 533), 15,
        )
    painter.text("RTT·Kafka 위치·Spark 시각은 서로 다른 처리 단계의 관측값입니다.", (56, 590), 13)


def draw_api(painter, slot, kind, scroll):
    response = slot.response or {}
    text = f"GET {QUERY_SPECS[kind].path}\nstatus: {response.get('status') or '—'}\n"
    text += json.dumps(response["json"], ensure_ascii=False, indent=2) if response.get("json") is not None else "조회 결과 없음"
    lines = []
    for line in text.splitlines():
        chunk = ""
        for char in line:
            if painter.fonts[13].size(chunk + char)[0] > 332:
                lines.append(chunk)
                chunk = ""
            chunk += char
        lines.append(chunk)
    scroll = max(0, min(scroll, max(0, len(lines) - 5)))
    clip = painter.canvas.get_clip()
    painter.canvas.set_clip(pygame.Rect(710, 647, 342, 124))
    for index, line in enumerate(lines[scroll:scroll + 5]):
        painter.text(line, (710, 647 + index * 23), 13)
    painter.canvas.set_clip(clip)


def draw_query_panels(painter, queries):
    draw_analytics(painter, queries["analytics"])
    draw_history(painter, queries["history"])
    draw_actions(painter, queries["actions"])
    draw_ingest(painter, queries["ingest"])
    draw_windows(painter, queries["windows"])
    draw_load(painter, queries["load"])
    draw_metrics(painter, queries["metrics"])
