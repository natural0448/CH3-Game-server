# server/game/ad_gateway.py

기존 서버 설정 ADS_BASE_URL·ADS_MEDIA_ID·ADS_MEDIA_KEY를 읽는다. 실제 키는 응답/접속기에 전달하지 않는다. 선택과 사건 모두 X-Media-ID/X-Media-Key를 붙이고 Player.pk를 공개 subject_id 문자열로 사용한다. 기존 request_decision은 직접 전송하며, 사건 함수는 같은 파일의 call_ads를 호출한다. request_ad_event 본문은 최신 23일차 3교시의 전체 완성 코드와 AST가 같다.

직접 호출의 기대 계약: Request는 JSON POST 요청, urlopen은 status/read를 제공하는 응답 stream, json.load/loads는 해석한 JSON 값이다. settings는 기존 Django 설정이며 이 계층에서 설정값을 변경하지 않는다. 외부 DB를 직접 호출하지 않는다.

## `class AdsUnavailable(Exception)`

기반 클래스: Exception. 메서드와 상태는 아래 계약을 따른다.

## `call_ads(path, payload)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| path | 없음 | ADS_BASE_URL에 붙이는 내부 API 경로 문자열. 현재 사건 호출은 /api/media/events/. |
| payload | 없음 | JSON으로 직렬화 가능한 요청 사전. subject와 사건 대상은 호출자가 구성한다. |

반환: `(HTTP 상태 int, 해석한 JSON 값)`. HTTPError에서는 허용된 오류 이름만 포함한 사전 또는 error=ad_request_rejected 사전이다. URLError·TimeoutError·JSON ValueError는 `(503, {"error": "ads_unavailable"})`다. 그 밖의 예외는 이 함수의 catch 범위 밖에서 전파된다.

의사코드: 기존 설정으로 URL·두 매체 헤더·JSON POST 구성 → timeout 3초로 urlopen → status와 json.load 결과 반환 → HTTPError 본문을 최대 65536 bytes 읽어 허용 오류 이름 추출 → 미허용 오류 문구를 일반 오류로 치환 → 지정된 통신/JSON 오류는 503 반환.

직접 호출: `Request`, `json.dumps`, `urlopen`, `json.load`, `json.loads`, `exc.read`, `body.get`, `error.split`, `isinstance`. HTTPError 오류 본문의 종류를 확인한 뒤 `.get()`을 호출한다. 성공 본문에는 별도의 크기 상한이 없으며 사건 receipt 검증은 request_ad_event가 맡는다.

## `request_decision(player, slot_id)`

2026-10-13 사용자 저장본은 25일차 7교시 제공 완성 함수와 AST가 같다. player는 기본값 없는 로그인 Player 객체, slot_id는 기본값 없는 슬롯 문자열이다. 이 함수는 slot_id를 자체 허용 목록으로 검사하지 않으며 실제 ad_views.ad_decision 호출자가 village-board/lobby-banner를 검사한다.

반환은 선택 응답 dict에 body 기본 빈 문자열·bid_amount(없으면 bid_units)를 보완한 사전이다. empty=True 또는 ad=None이면 원래 응답을 보존하고 ad=None을 넣어 반환한다. 서버 키 없음은 AdsUnavailable(media_key_missing), 선택 호출의 HTTP/통신/파싱/슬롯 오류는 AdsUnavailable(ads_unavailable)이다. context 조회 실패도 호출자에게 전파된다.

의사코드: 서버 설정 매체/키 검사 → request_context(player) 공개 복사본을 payload.context에 넣기 → 두 매체 헤더와 top-level media_id로 /api/media/decision/ POST → timeout 1.5초 → JSON 사전·빈 광고·동일 슬롯 검사 → 응답 반환. 직접 호출은 request_context, Request, json.dumps/json.load, urlopen, dict.get다. 요청 URL은 ADS_BASE_URL.rstrip('/')에서 시작한다. 과거 본문의 read 상한·금액·소재 검사와 context={} 설명은 현재 함수에 해당하지 않는다. 이 계층은 DB를 쓰지 않으며 광고 서버 선택 서비스가 결정 저장을 맡는다.

## `request_ad_event(player, decision_id, event_type)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| player | 없음 | 로그인 세션의 Django Player 객체; pk를 subject_id로 변환. |
| decision_id | 없음 | 선택 결정 ID 문자열; 이벤트 중계는1..128자. |
| event_type | 없음 | impression 또는 click 문자열. |

반환: event_id·event_type·created 세 필드만 있는 dict. created의 True/False 모두 허용한다. 입력/거절은 ValueError, 빈 서버 키는 AdsUnavailable(media_key_missing), status 503은 AdsUnavailable(ads_unavailable), 잘못된 200 본문은 AdsUnavailable(invalid_ad_event_response)다.

의사코드: 서버 키 검사 → ID 1..128자·종류 검사 → 설정의 매체 ID와 str(player.pk)로 payload 구성 → call_ads로 /api/media/events/ 호출 → 503 구별 → 200 외에는 사전 여부 확인 후 허용 오류만 ValueError로 전달 → 200은 사전·동일 사건 ID·동일 종류·created bool 검사 → 공개 세 필드 반환.

직접 호출: `call_ads`, `AdsUnavailable`, `ValueError`, `data.get`, `isinstance`, `len`, `str`, `type`. call_ads는 상태와 JSON 두 값을 반환한다. 허용 오류는 decision_snapshot_missing·decision_not_found_for_subject·impression_required·decision_id_required·event_type_invalid이며 그 외는 ad_event_rejected다. 로그인 Player 조회와 HTTP 응답 변환은 호출하는 ad_views.ad_event의 책임이다.

## `request_context(player)`

player는 기본값 없는 로그인 Player 객체다. 반환은 검증한 공개 context의 새 dict이며 문서 없음·삭제 상태의 {}도 허용한다. 서버 키 없음은 AdsUnavailable(media_key_missing), HTTP/통신/응답 계약 오류는 AdsUnavailable(ads_unavailable)이다.

의사코드: settings.ADS_MEDIA_ID와 str(player.pk)로 subject → subject-only payload → JSON·Accept·X-Media-ID·X-Media-Key 헤더 → /api/media/context/ POST(timeout=1.5초) → 응답 subject 동일·context 사전 검사 → 비어 있지 않으면 정확한 다섯 필드·동일 ID·타입·version>=0·aware ISO 시각 검사 → dict(context). 직접 호출은 Request, json.dumps(allow_nan=False), urlopen, json.load, datetime.fromisoformat, dict다. 매체 키의 출처는 서버 settings이며 응답으로 복사하지 않는다. 두 HTTP 호출의 timeout을 전체 원자 작업/deadline으로 해석하지 않는다.

현재 함수는 교안 AST와 같고 후속 수정에서도 본문을 보존했다. 광고 인증이 헤더 기반으로 연결돼 subject-only payload를 받아들이며 /api/media/context/도 등록됐다. 현재 context 조회 다음 선택 요청에 해당 공개 사전을 넣는 순서와 각각 1.5초 timeout을 테스트에서 확인했다.

## 상태·값 출처

CREATIVE_PATHS는 빈 문자열·/static/ads/creatives/forest-tools.png·/static/ads/creatives/camp-tea.png의 frozenset이다. ADS_BASE_URL·ADS_MEDIA_ID·ADS_MEDIA_KEY는 기존 서버 설정에서 읽는다. request/payload/status/data와 allowed 집합은 해당 함수가 생성·소유한다. subject_id의 출처는 로그인 Player.pk, decision_id와 event_type의 출처는 호출자의 검증된 사건 입력이다. 이 계층은 snapshot이나 사건을 DB에 쓰지 않는다. 비밀값·쿠키·CSRF 토큰은 문서/증거에 복사하지 않는다.
