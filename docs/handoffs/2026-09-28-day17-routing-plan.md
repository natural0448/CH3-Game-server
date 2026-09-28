# 17일차 라우팅·기획 정합화 인수인계

## 요청 목적과 완료 결과

17일차의 Kafka 확정 행동, Delta 고유 저장, raw/delta 집계, 분석 API와 Spark Worker 운영을 하나의 구현 기획으로 정리하고 관련 서버 라우팅 문서를 실제 코드와 맞췄다. 이 작업에서는 서버 코드를 수정하지 않았다.

## 작업 시작 전 Git 상태

- 저장소: `C:\MLO01-01\Chapter3\Game-server`
- 직전 커밋: `27f2bc2 day17 - commit`
- staged 변경: 없음
- 작업 시작 전에 존재한 modified: `docs/server-routing/README.md`, run/summarize/start-dev 짝 문서, `run_game_delta.py`, `summarize_game.py`, `game_batch.py`, `start-dev.ps1`, `한번에_실행.md`
- 작업 시작 전에 존재한 untracked: `2026-09-28-delta-batch-summary.md`, `2026-09-28-second-spark-worker.md`, `files/spark_jobs/game_batch.py.md`

기존 변경은 사용자 작업으로 취급해 보존했다. README는 기존 변경과 겹치며 이번 작업에서는 17일차 기획 링크만 추가했다.

## 이번 작업의 문서 변경

- 추가: `docs/server-routing/day17-delta-plan.md`
- 수정: `docs/server-routing/README.md`
- 수정: `docs/server-routing/files/spark_jobs/game_actions_delta.py.md`
- 수정: `docs/server-routing/files/server/analytics/views.py.md`
- 추가: `docs/handoffs/2026-09-28-day17-routing-plan.md`

## 정리한 설계

- MySQL/outbox → game.events.v1 → Python 변환 → game.actions.v1 → Delta silver → raw/delta batch summary → 인증된 분석 API 흐름
- Delta의 `event_id` 고유성, checkpoint·progress·snapshot 경계
- `record_count`와 `event_count`의 서로 다른 의미
- Windows Kafka cleaner·retention 비활성화와 오프라인 디스크 정리 책임
- NiFi 미사용 프로필의 Worker 2와 Delta stream의 executor core 1 배치
- 현재 구현되지 않은 자동 스케줄·vacuum·모델 학습·Spark 실행 API의 범위 제외

## 라우팅 정합화

- `game_actions_delta.py` 문서의 MERGE 실행 주체를 실제 코드인 `batch.sparkSession`으로 바로잡았다.
- `summary_view` 문서에 게시 JSON의 source, record_count, event_count와 배열 필드를 기록했다.
- 서버 색인에서 17일차 통합 기획으로 진입할 수 있게 했다.

## 검사 결과

- 서버 라우팅 Markdown 링크 검사: 통과
- `python manage.py check`: 통과
- 관련 Django/Spark Python 파일 `py_compile`: 통과
- `git diff --check`: 통과

## 남은 확인

실제 Spark/Kafka 작업은 문서 작업 중 새로 실행하지 않았다. 운영 확인은 기획 문서의 실행 순서대로 수행하고 Master UI, progress JSON, game-summary.json과 `/api/analytics/` 값을 대조한다.
