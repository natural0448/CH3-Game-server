# `tools/ws_load.py`

## 책임과 호출 경계

로컬 Django 서버에 수업 계정별 독립 세션으로 로그인하고 `/ws/play/`에서 한 번에 하나의 이동 명령을 보내 연결 수, 성공 수와 RTT를 JSON으로 저장한다. 서버 상태·인증 정책·게임 규칙을 변경하지 않는다.

## 함수

### `resolve_project_path(value) -> Path`

- `value`: 명령줄에서 받은 문자열 또는 Path형 경로.

절대경로는 그대로 정규화한다. 상대경로의 선두 `.`·`..`를 제외했을 때 첫 폴더가 `data`이면 `PROJECT_DIR/data/...`로 해석한다. 그 밖의 상대경로는 현재 작업 디렉터리 기준으로 해석한다. 이 규칙으로 `Game-server`와 `Game-server/server` 어느 위치에서 실행해도 `data/load/...`와 `../data/load/...`가 같은 프로젝트 데이터 폴더를 가리킨다.

### `utc_now() -> str`

UTC 현재 시각을 ISO 문자열로 반환한다. `datetime.now(timezone.utc)`를 직접 호출한다.

### `nearest_rank(values, fraction) -> float | None`

- `values`: RTT 숫자 목록.
- `fraction`: 선택할 누적 비율.

빈 목록은 `None`, 그 외에는 정렬 후 nearest-rank 위치의 값을 반환한다.

### `csrf_token(session, base_url) -> str`

기존 `aiohttp.ClientSession`으로 CSRF GET을 보내고 200 JSON의 `csrfToken`을 검증해 반환한다.

### `login(session, base_url, username, password) -> dict`

CSRF 조회 → JSON 로그인 POST → CSRF 재조회 → 현재 Player GET 순서로 호출하고 Player 상태를 반환한다. redirect를 따르지 않는다.

### `read_until(socket, condition, timeout_seconds) -> dict`

한 deadline 안에서 WebSocket 메시지를 읽고 `condition`이 참인 첫 JSON을 반환한다. 닫힘·오류·시간 초과는 예외로 전달한다.

### `run_player(account, password, options, gate, ready, shared) -> dict`

```text
계정별 report와 독립 CookieJar/ClientSession 생성
HTTP 로그인 후 WebSocket 연결
첫 snapshot을 기다리고 연결 수와 peak 갱신
공통 gate 이후 seconds 동안 UUID 이동 명령 전송
같은 command_id의 state/error만 기다림
성공 RTT와 시도·성공·오류 수 기록
종료 시 열린 연결 수 감소
계정별 report 반환
```

### `run_load(accounts, password, options) -> None`

계정별 task를 0.1초 간격으로 만들고 준비 신호 뒤 동시에 측정을 시작한다. 집계 지표와 계정별 공개 결과를 JSON 임시 파일에 쓴 뒤 `--output`으로 교체한다.

### `main() -> None`

```text
필수 accounts/output과 측정 옵션 및 한글 도움말 파싱
base-url을 로컬 HTTP origin으로 제한
clients 1..200, seconds 5..120, interval 0.5 이상 검사
resolve_project_path로 accounts/output을 프로젝트 구조에 맞게 정규화
accounts 파일 누락·UTF-8 JSON 오류를 argparse 오류로 표시
요청 계정 수와 username 고유성 검사
getpass로 비밀번호 입력
asyncio.run을 한 번 호출
```

## 주요 변수와 값의 출처

- `options.base_url`: 기본 `http://127.0.0.1:8000`, 외부 호스트는 거부.
- `PROJECT_DIR`: 이 파일의 부모인 `tools`의 부모, 즉 `Game-server` 절대경로.
- `options.accounts`: `resolve_project_path`가 정규화한 계정 JSON 절대경로.
- `options.output`: `resolve_project_path`가 정규화한 결과 JSON 절대경로.
- `password`: `getpass` 입력이며 결과와 로그에 저장하지 않는다.
- `shared`: 현재 열린 연결 수와 관찰 peak의 task 공유 사전.
- `rtt_ms`: 계정별 내부 계산 목록이며 공개 `by_player`에서는 제거한다.
