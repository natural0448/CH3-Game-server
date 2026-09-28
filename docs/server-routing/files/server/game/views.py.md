# `server/game/views.py`

## 책임과 호출 경계

로컬 전달 관리 화면과 로그인 사용자의 Player·이력·전달 상태 JSON을 제공한다. 파일 끝에는 별도 CSRF·로그인 view도 정의되어 있지만 현재 URL 순서에서는 `game.auth_views`의 동일 경로가 먼저 선택된다.

## 함수

### `delivery_dashboard(request) -> HttpResponse`

로컬 연결 주소만 허용하고, 전체 GameEvent의 total/pending/sent를 집계한다. 쿼리의 `status`에 따라 행을 거른 뒤 20개씩 페이지 처리하여 템플릿을 렌더링한다.

### `player_view(request) -> JsonResponse`

비로그인은 401 JSON을 반환한다. 로그인 사용자 Player를 찾아 `serialize_player` 결과를 반환한다.

### `play(request) -> HttpResponse`

`login_required`를 통과한 요청에 `game/play.html`을 렌더링한다.

### `history(request) -> JsonResponse`

비로그인은 401을 반환한다. 현재 사용자의 최근 GameEvent 20개를 `serialize_event`로 변환해 반환한다.

### `delivery_view(request) -> JsonResponse`

현재 사용자의 전체 사건 수와 `published_at`이 없는 대기 사건 수를 반환한다.

### `csrf_view(request) -> JsonResponse`

GET 요청에 `get_token(request)` 결과를 `csrfToken`으로 반환하고 CSRF 쿠키를 보장한다. 현재 중복 URL 뒤쪽에 있어 기본 resolver로는 선택되지 않는다.

### `api_login(request) -> JsonResponse`

POST JSON의 username/password 타입을 확인하고 `authenticate`와 `auth_login`을 호출한다. 잘못된 JSON은 400, 인증 실패는 401, 성공은 `authenticated=true`를 반환한다. 현재 중복 URL 뒤쪽에 있어 기본 resolver로는 선택되지 않는다.

## 주요 값의 출처

- `REMOTE_ADDR`: 로컬 관리 화면 접근 판정.
- `status`: 쿼리 문자열의 `all`, `pending`, `sent` 중 하나.
- `checked_at`: `timezone.now()`.
- Player와 GameEvent: MySQL의 Django ORM 조회 결과.
