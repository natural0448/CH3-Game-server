# server/game/ad_views.py

기존 ad_views.py에 수정 교안의 ad_events.ad_event 함수를 그대로 적용하고 기존 game.urls 경로를 사용한다. 게임 세션 User의 Player가 서버간 공개 수신자이며 본문 subject/player_id로 바꿀 수 없다. ad_event는 decision_id·event_type 두 필드만 받는다. 기존 CSRF 정책을 적용하며 인증401, 이벤트 Player 없음409, 공개 입력 오류400, 광고 장애503, 성공no-store. 기존 decision은 Player 없음404 및 기존 이미지 선택 경로를 유지한다.

직접 호출의 기대 계약: get_db는 기존 Database, find_one은 dict/None, find·sort·limit는 Cursor, update_one은 UpdateResult, insert_one은 InsertOneResult, create_index는 색인 이름이다. Django render/JsonResponse는 HttpResponse, JSON parse는 dict 등 JSON 값, urlopen은 응답 stream, patch/assert는 테스트 fixture/검증을 제공한다. 하위 계층 내부는 해당 짝 문서에 있다.

## `ad_preview(request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | Django HttpRequest; decorator가 로그인/메서드/CSRF 또는 매체 인증을 검사한다. |

반환·실패: HTML200 또는 로그인302/메서드405.

의사코드: 로그인/GET → 기존 preview template render.

직접 호출: `render`.

Decorator: `login_required`, `require_GET`.

## `ad_decision(request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | Django HttpRequest; decorator가 로그인/메서드/CSRF 또는 매체 인증을 검사한다. |

반환·실패: JSON200/400/401/404/503; CSRF403/메서드405.

의사코드: POST/로그인 → User의 Player → JSON/슬롯 → request_decision → 공개 JSON.

직접 호출: `JsonResponse`, `Player.objects.filter`, `Player.objects.filter(user=request.user).first`, `isinstance`, `json.loads`, `payload.get`, `request_decision`.

Decorator: `require_POST`.

## `ad_event(request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | Django HttpRequest; decorator가 로그인/메서드/CSRF 또는 매체 인증을 검사한다. |

반환·실패: JSON200/400/401/409/503; CSRF403/메서드405.

의사코드: POST/로그인 → User의 Player → 정확한 두 필드 JSON → request_ad_event → no-store JSON; 허용 오류만 공개.

직접 호출: `JsonResponse`, `Player.objects.filter`, `Player.objects.filter(user=request.user).first`, `ValueError`, `isinstance`, `json.loads`, `request_ad_event`, `set`, `str`.

Decorator: `require_POST`.

## 상태·값 출처

지역 변수는 해당 함수가 소유하며 request/입력·서버 설정·DB 조회 또는 위 의사코드의 생성 단계에서 얻는다. 저장 snapshot과 receipt의 쓰기는 서비스/사건 계층이 맡는다. 테스트 연결·patch·가짜 응답은 해당 테스트 클래스만 소유하고 정리한다. 비밀값·쿠키·CSRF 토큰은 문서/증거에 복사하지 않는다.
