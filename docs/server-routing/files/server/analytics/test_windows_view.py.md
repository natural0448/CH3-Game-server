# `server/analytics/test_windows_view.py`

## 책임

시간 창 URL과 읽기 전용 API 계약을 회귀 검사한다.

## 클래스와 메서드

### `WindowsContractTests(SimpleTestCase)`

- `setUp(self) -> None`: 인증된 가짜 GET 요청을 만든다.
- `test_url_resolves_to_windows_view(self) -> None`: `/api/analytics/windows/`가 `windows_view`에 연결되는지 확인한다.
- `test_missing_and_published_snapshot_are_read_only(self) -> None`: 파일 미생성 응답과 게시 JSON 응답을 확인하고 `subprocess.run`이 호출되지 않았음을 검사한다.
- `test_login_is_required(self) -> None`: 미인증 요청의 401 JSON을 확인한다.

직접 호출: Django `RequestFactory`, `resolve`, `override_settings`, `TemporaryDirectory`, `unittest.mock.patch`.

