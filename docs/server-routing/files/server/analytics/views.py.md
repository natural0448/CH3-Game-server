# `server/analytics/views.py`

## 책임

로그인한 사용자가 이미 게시된 분석 JSON을 GET으로 읽도록 한다. 뷰는 Spark 작업이나 Kafka 요청을 실행하지 않는다.

## 함수

### `summary_view(request) -> JsonResponse`

인증되지 않은 요청에는 401을 반환한다. `settings.DATA_DIR/marts/game-summary.json`이 없으면 미생성 상태를, 있으면 파일의 요약을 `available=true`와 함께 반환한다.

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

