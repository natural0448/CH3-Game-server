# server/game/ad_views.py

게임의 로그인 세션에서 Player를 찾아 광고 선택·사건을 중계하고 미리보기 HTML을 제공한다. 기존 `game.urls` 경로를 사용한다. 게임 세션 User의 Player가 서버간 공개 수신자이며 본문 subject/player_id로 바꿀 수 없다. `ad_event`는 decision_id·event_type 두 필드만 받는다. 기존 Django CSRF middleware를 적용하며 인증401, 이벤트 Player 없음409, 공개 입력 오류400, 광고 장애503, 이벤트 성공no-store다. 기존 decision은 Player 없음404 및 기존 이미지 선택 경로를 유지한다.

직접 호출의 기대 계약: `Player.objects.filter(user=request.user).first()`는 Player 또는 None, `render`는 HttpResponse, `JsonResponse`는 JSON HttpResponse, `json.loads`는 해석한 JSON 값이다. `request_decision`은 공개 선택 dict 또는 ad:null dict, `request_ad_event`는 공개 event_id·event_type·created dict를 반환한다. 이 모듈은 Django ORM으로 Player를 읽고 gateway를 호출한다. MongoDB와 HTTP 전송의 직접 호출은 없으며 광고 서버 저장과 gateway 내부 통신은 각 하위 계층 문서의 책임이다.

## `ad_preview(request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | Django HttpRequest; `login_required`와 `require_GET`가 로그인·GET을 검사한다. |

반환·실패: HTML200 또는 로그인302/메서드405.

의사코드: 로그인/GET → 기존 preview template render.

직접 호출: `render`.

Decorator: `login_required`, `require_GET`.

## `ad_decision(request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | Django HttpRequest; `require_POST`가 메서드를, 함수가 로그인·Player·JSON·slot_id를 검사한다. |

반환·실패: JSON200/400/401/404/503; CSRF403/메서드405.

의사코드: POST/로그인 → User의 Player → request.body JSON을 dict로 해석 → slot_id가 village-board/lobby-banner인지 검사 → request_decision → 공개 JSON. JSON 해석·dict 타입 실패는 invalid_json, 누락/다른 slot_id는 invalid_slot이다. dict의 다른 키는 이 함수가 공개 수신자 판정에 사용하지 않는다.

직접 호출: `JsonResponse`, `Player.objects.filter`, `Player.objects.filter(user=request.user).first`, `isinstance`, `json.loads`, `payload.get`, `request_decision`.

Decorator: `require_POST`.

## `ad_event(request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | Django HttpRequest; `require_POST`가 메서드를, 함수가 로그인·Player·JSON의 정확한 두 키를 검사한다. |

반환·실패: JSON200/400/401/409/503; CSRF403/메서드405.

의사코드: POST/로그인 → User의 Player → 정확한 두 필드 JSON → request_ad_event → no-store JSON; 허용 오류만 공개.

직접 호출: `JsonResponse`, `Player.objects.filter`, `Player.objects.filter(user=request.user).first`, `ValueError`, `isinstance`, `json.loads`, `request_ad_event`, `set`, `str`.

Decorator: `require_POST`.

## 상태·값 출처

지역 변수는 해당 함수가 소유한다. `player`는 로그인 User의 ORM 조회 결과, `payload`/`body`는 request.body의 JSON, `slot_id`는 payload의 값, `data`는 gateway 반환값이다. `allowed`는 ad_event가 소유한 decision_snapshot_missing·decision_not_found_for_subject·impression_required·decision_id_required·event_type_invalid 집합이며 다른 ValueError/UnicodeDecodeError는 ad_event_rejected로 응답한다. 성공 이벤트 response에만 Cache-Control=no-store를 설정한다. 광고 선택 snapshot과 사건 receipt의 쓰기는 광고 서버가 맡는다. 24일차 Player 공개 snapshot 파일 생산은 별도 게임 관리 명령의 책임이다. 비밀값·쿠키·CSRF 토큰은 문서/증거에 복사하지 않는다.
