# `server/game/urls.py`

## 책임과 호출 경계

게임 앱의 HTTP 경로를 각 view callable에 연결한다. WebSocket `/ws/play/`는 이 파일이 아니라 `game/routing.py`가 담당한다.

## 변수

### `app_name: str = "game"`

URL reverse namespace의 출처다.

### `urlpatterns: list`

```text
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

직접 호출: `django.urls.path`와 `game.auth_views`, `game.views`의 view callable.

## 22일차 이미지 광고 최종 반영

기존 game/auth 경로에 GET /ads/preview/→ad_views.ad_preview와 POST /api/ads/decision/→ad_views.ad_decision을 추가한다. 기존 root URL include와 충돌하지 않으며 다른 경로는 그대로다.
