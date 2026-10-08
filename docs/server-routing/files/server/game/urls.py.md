# `server/game/urls.py`

## 책임과 호출 경계

게임 앱의 HTTP 경로를 각 view callable에 연결한다. WebSocket `/ws/play/`는 이 파일이 아니라 `game/routing.py`가 담당한다.

## 변수

### `app_name: str = "game"`

URL reverse namespace의 출처다.

### `urlpatterns: list`

```text
/ads/preview/ -> ad_views.ad_preview (name=ad-preview)
/api/ads/decision/ -> ad_views.ad_decision (name=ad-decision)
/api/ads/events/ -> ad_views.ad_event (name=ad-events)
/ -> views.delivery_dashboard
/api/auth/csrf/ -> auth_views.csrf_token
/api/auth/login/ -> auth_views.login_view
/api/auth/logout/ -> auth_views.logout_view
/play/ -> views.play
/api/player/ -> views.player_view
/api/delivery/ -> views.delivery_view
/api/history/ -> views.history
/api/auth/csrf/ -> views.csrf_view
/api/auth/login/ -> views.api_login
```

같은 인증 경로가 뒤에 다시 등록되어 있으나 Django URL resolver는 먼저 일치한 `auth_views` 경로를 선택한다. 따라서 뒤의 `views.csrf_view`와 `views.api_login`은 현재 경로 순서에서 도달하지 않는다.

직접 호출: `django.urls.path`와 `game.ad_views`, `game.auth_views`, `game.views`의 view callable. `path`는 URLPattern을 만들고 이 목록은 Django가 읽는다. 광고 선택과 사건의 Player 조회·입력 검사·HTTP 변환은 `ad_views`가, 광고 서버 요청은 `ad_gateway`가 담당한다.

## 23일차 1~2교시 최종 반영

기존 게임·인증·조회·광고 선택·미리보기 경로를 유지하고 `api/ads/events/`를 `ad_event(name=ad-events)`에 연결한다. 이 파일은 static 경로를 등록하지 않는다. `urlpatterns`의 쓰기 소유자는 이 모듈이며 위 순서로 선언한 `path` 목록이다. 24일차 snapshot 내보내기는 관리 명령이므로 HTTP 경로를 추가하지 않는다.
