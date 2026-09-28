# `server/analytics/test_day18_snapshots.py`

## 책임

18일차 운영 지표와 부하 측정 snapshot API가 로그인한 GET에서 저장 파일만 읽고, 미생성 상태를 0으로 꾸미지 않으며, 계정별 상세 행을 노출하지 않는지 검사한다.

## 클래스와 메서드

### `Day18SnapshotViewTests.request(self, path, authenticated=True)`

파라미터 `path`는 검사할 API 경로이고 `authenticated`는 테스트 user의 로그인 여부이며 기본값은 `True`다. `RequestFactory` GET에 해당 인증 상태를 가진 user를 붙인 request를 반환한다.

### `Day18SnapshotViewTests.test_urls_resolve(self) -> None`

```text
resolve로 /api/analytics/load/와 /api/analytics/metrics/ 조회
각 경로가 load_snapshot과 metrics_snapshot을 직접 가리키는지 확인
```

### `Day18SnapshotViewTests.test_missing_snapshots_are_not_reported_as_zero(self) -> None`

```text
빈 임시 DATA_DIR에서 두 view 호출
각 응답이 available=false이고 snapshot 값은 null인지 확인
미생성 상태가 숫자 0으로 바뀌지 않는지 확인
```

### `Day18SnapshotViewTests.test_load_snapshot_projects_room_totals_without_player_rows(self) -> None`

```text
임시 run-50.json에 계정별 측정 행과 비공개 environment 작성
load_snapshot 호출 중 subprocess가 실행되지 않았는지 확인
응답에서 by_player와 environment가 제거됐는지 확인
room_id별 connected와 success_count 합계를 확인
```

### `Day18SnapshotViewTests.test_metrics_snapshot_reads_published_json_without_running_work(self) -> None`

```text
임시 game-metrics.json 작성
metrics_snapshot 호출 중 subprocess가 실행되지 않았는지 확인
게시된 JSON이 available=true의 metrics 값으로 그대로 반환되는지 확인
```

### `Day18SnapshotViewTests.test_login_is_required(self) -> None`

```text
인증되지 않은 request로 load_snapshot과 metrics_snapshot 호출
두 응답이 모두 로그인 redirect 302인지 확인
```

직접 호출: `RequestFactory`, `resolve`, `override_settings`, `TemporaryDirectory`, `unittest.mock.patch`, `load_snapshot`, `metrics_snapshot`.
