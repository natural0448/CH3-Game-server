# 2026-09-28 서버·분석 파이프라인 현재 구현 정본

상태: **구현 반영 / 검증 완료**  
기준 저장소: `C:/MLO01-01/Chapter3/Game-server`  
기준 커밋: `ed45ba4 day17-finish` + 아래 작업 트리 변경

이 문서는 2026-09-28 종료 시점의 서버, Kafka→Delta 분석 흐름, 동시 접속 측정과 읽기 전용 API 상태를 한 곳에서 찾기 위한 정본이다. 함수별 세부 계약은 `docs/server-routing/README.md`와 각 1:1 짝 문서를 기준으로 한다. 이전 인수인계 문서는 작업 과정과 원인 분석 기록으로 유지한다.

## 1. 완료된 동작

```text
게임 확정 사실(GameEvent)
  → publisher가 game.events.v1에 전달
  → Python 변환기가 action_label을 붙여 game.actions.v1에 전달
  → Spark streaming이 event_id 기준 Delta 고유 사실로 저장
  → summarize_game --source delta가 game-summary.json 게시

수업용 계정 준비
  → ws_load.py가 로그인·WebSocket 이동을 동시 측정
  → run-20.json / run-50.json 저장
  → compare_load.py가 같은 조건의 결과 비교

collect_game_metrics
  → MySQL 최근 확정 사실·publisher 상태 조회
  → Kafka group committed/end offset 조회
  → 기존 Spark progress 파일 조회
  → game-metrics.json 원자적 게시

로그인한 GET
  → /api/analytics/load/에서 완료된 run-50 요약 읽기
  → /api/analytics/metrics/에서 게시된 운영 snapshot 읽기

Lake 인계
  → export_game_handoff가 MySQL GameEvent를 UTF-8 JSONL로 내보내기
  → event_id·event_time·payload와 실제 DB 출처 계약 보존
  → data/handoff/day18/README.md에 범위·실행·종료 순서 기록
```

HTTP 조회는 부하 측정, Kafka consume, Spark 작업을 시작하지 않는다. 계정별 부하 행과 실행 환경 상세는 `/api/analytics/load/` 응답에서 제거하고 방별 연결·성공 합계만 제공한다. 미생성 snapshot은 `available=false`와 `null`로 구분하며 숫자 0을 만들지 않는다.

## 2. 오늘 작업 트리의 개발 파일

### 수정

- `server/game/urls.py`, `server/game/views.py`: 로컬 전달 현황과 기존 게임·인증·Player API 경로.
- `server/analytics/urls.py`, `server/analytics/views.py`: 운영 지표·부하 측정 snapshot GET.
- `tools/measurement-notes.md`: 20명·50명 측정값, 해석 범위와 재현 순서.

### 추가

- `server/game/management/commands/prepare_load_players.py`: 수업용 계정·방 배치와 비밀번호 없는 계정 목록 생성.
- `server/game/management/commands/export_game_handoff.py`: 선택한 DB 확정 사실 범위를 JSONL Lake 원본으로 내보내기.
- `tools/ws_load.py`: 인증 session과 WebSocket을 사용한 동시 접속 측정.
- `tools/read_load_result.py`: 저장된 단일 결과의 대표 지표 출력.
- `tools/compare_load.py`: 동일 조건 두 결과의 처리율·RTT 비교.
- `server/analytics/management/commands/collect_game_metrics.py`: DB·Kafka·Spark progress 운영 snapshot 게시.
- `server/analytics/test_day18_snapshots.py`: 두 신규 API의 경로·인증·미생성·필드 제한 회귀 검사.
- `server/game/test_handoff_export.py`: JSONL 정렬·필드·반개구간·timezone·Kafka 위치 부재 계약 검사.

위 파일의 짝 문서와 `docs/server-routing/README.md` 색인을 현재 코드에 맞췄다. 데이터 백업·Delta checkpoint·집계 결과는 실행 산출물이며 라우팅 개발 파일로 취급하지 않는다.

## 3. 현재 게시된 측정 정본

| 항목 | 20명 측정 | 50명 요청 측정 |
| --- | ---: | ---: |
| 조건 | 30초, 1초 간격 | 30초, 1초 간격 |
| 연결 성공 / peak | 20 / 20 | 48 / 48 |
| 성공 명령 | 600 | 1,484 |
| 오류 | 0 | 2 |
| 성공 처리율 | 19.988/s | 48.713/s |
| RTT p95 | 340.282ms | 500.036ms |

50명 요청 결과는 실제 연결 48명 측정이다. 현재 온라인 인원이나 서버 최대 수용량을 뜻하지 않는다.

`data/marts/game-summary.json`은 `source=delta`, `record_count=5707`, `event_count=5707`인 고유 사실 집계다. 현재 `data/marts/game-metrics.json`은 120초 관찰 snapshot이며 Kafka 세 partition의 확인된 lag 합계가 0이다. 그 120초 구간에 새 확정 사실이 없어 `confirmed_count=0`이며, 이는 미생성 상태와 다른 실제 관찰값이다.

`data/handoff/day18/game-events.jsonl`은 DB 전체 범위 5,968행이며 고유 `event_id`도 5,968개다. 이 DB export와 위 Delta summary는 생성 시각과 원천 경계가 다르므로 count를 같은 snapshot처럼 비교하지 않는다. 실제 출처·범위·필드와 누적 실행 순서는 같은 폴더의 `README.md`에 기록했다.

## 4. Git 기준과 변경 소유권

- 작업 시작·종료 기준 커밋: `ed45ba4 day17-finish`.
- staged 변경: 없음.
- 작업 시작 전에 이미 존재했던 변경은 사용자 작업으로 취급했다. 특히 game URL/view, 계정 준비, 초기 부하 도구와 측정 기록을 되돌리지 않았다.
- 오늘 이어서 완성한 관리명령, 분석 API, 비교 도구, 회귀 테스트와 문서는 기존 변경 위에 추가됐다.
- 비밀번호, Cookie, session, CSRF와 `.env` 값은 코드 diff와 문서에 복사하지 않았다.

## 5. 라우팅 문서 정합화

- 색인: `docs/server-routing/README.md`.
- 오늘 변경된 모든 개발 파일에 `docs/server-routing/files/<개발 파일 상대경로>.md` 짝 문서가 있다.
- 짝 문서는 실제 시그니처, 파라미터·기본값, 의사코드, 직접 호출과 주요 값 출처를 기록한다.
- `server/analytics/test_day18_snapshots.py`의 여섯 메서드도 개별 시그니처와 검사 흐름으로 정리했다.
- 계획 문서와 과거 인수인계는 현재 구조의 세부 정본으로 사용하지 않는다. 현재 파일 구조는 라우팅 색인과 짝 문서를 우선한다.

## 6. 검증 결과

```text
python manage.py check
결과: System check identified no issues

python manage.py test analytics
결과: 12 tests passed

python manage.py test game.test_handoff_export
결과: 2 tests passed

python -m py_compile analytics/management/commands/collect_game_metrics.py analytics/views.py analytics/urls.py
python -m py_compile ../tools/compare_load.py ../tools/read_load_result.py ../tools/ws_load.py
결과: 성공

python ../tools/compare_load.py ../data/load/run-20.json ../data/load/run-50.json
결과: 동일 30초/1초 조건, 저장 결과 비교 성공
```

Delta checksum 복구 후 `summarize_game --source delta`와 `run_game_delta` Kafka lag 0까지의 검증은 `2026-09-28-delta-checksum-repair.md`에 남아 있다. 새 비밀번호 입력이 필요한 부하 측정과 실제 GUI 로그인은 반복하지 않았다.

## 7. 다음 시작 순서

운영 지표 snapshot을 갱신한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server\server
.\.venv\Scripts\python.exe manage.py collect_game_metrics --seconds 120 --topic game.events.v1 --group village-actions-v1
```

Django를 재시작한 뒤 로그인한 클라이언트에서 `최근 수업 측정`과 `분석 전달 상태`를 누른다. Delta streaming이 필요한 수업에서는 Spark master·worker와 Kafka broker를 먼저 실행하고 별도 PowerShell에서 `python manage.py run_game_delta`를 지속 실행한다.

Lake 인계 원본을 현재 DB 범위로 다시 만들 때 실행한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server\server
.\.venv\Scripts\python.exe manage.py export_game_handoff --output ..\data\handoff\day18\game-events.jsonl
```

클라이언트의 같은 날짜 정본은 `C:/MLO01-01/Chapter3/Game-client/docs/handoffs/2026-09-28-day18-canonical.md`다.
