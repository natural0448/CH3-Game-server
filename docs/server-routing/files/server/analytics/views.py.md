# `server/analytics/views.py`

## 책임

로그인한 사용자가 이미 게시된 분석 JSON을 GET으로 읽도록 한다. 뷰는 Spark 작업이나 Kafka 요청을 실행하지 않는다.

## 함수

### `summary_view(request) -> JsonResponse`

인증되지 않은 요청에는 401을 반환한다. `settings.DATA_DIR/marts/game-summary.json`이 없으면 `available=false`와 미생성 이유를 반환한다. 파일이 있으면 `available=true`와 함께 게시 파일의 `schema_version`, `generated_at`, `source`, `record_count`, `event_count`, `by_action`, `by_room`을 반환한다. 이 뷰는 필드 값을 다시 계산하거나 Spark 작업을 실행하지 않는다.

### `windows_view(request) -> JsonResponse`

```text
request.user가 인증되지 않았으면 {error: login_required}, 401 반환
settings.DATA_DIR/marts/windows.json이 없으면 {available: false, windows: []} 반환
파일을 UTF-8 JSON으로 읽음
{available: true, generated_at, windows} 반환
```

반환되는 `windows` 행은 게시 파일에서 온 `kind`, `window_start`, `window_end`, `event_type`, `count`를 유지한다. 직접 호출하는 외부 코드는 `settings.DATA_DIR`, `Path.read_text`, `json.loads`, `JsonResponse`이다.

### `actions_snapshot(request) -> JsonResponse`

로그인한 사용자의 고정 Kafka snapshot 집계와 manifest를 읽고 행동 표시명을 붙여 반환한다. 직접 호출하는 외부 코드는 Django `login_required`, `ACTION_LABELS`, 파일 JSON 읽기다.

### `metrics_snapshot(request) -> JsonResponse`

```text
GET·로그인 조건 검사
DATA_DIR/marts/game-metrics.json이 없으면 {available:false, metrics:null}
있으면 UTF-8 JSON을 읽어 {available:true, metrics:report}
Kafka 조회나 Spark 작업을 실행하지 않음
```

### `load_snapshot(request) -> JsonResponse`

```text
GET·로그인 조건 검사
DATA_DIR/load/run-50.json이 없으면 {available:false, load:null}
있으면 LOAD_SNAPSHOT_FIELDS의 완료 측정 필드만 복사
by_player를 room_id별 connected/success_count 작은 목록으로 축약
계정별 행과 environment는 HTTP 응답에서 제외
```

`LOAD_SNAPSHOT_FIELDS`는 생성·시작 시각, profile, 연결·요청·성공·오류·경과·처리율·RTT 필드의 허용 목록이다.
