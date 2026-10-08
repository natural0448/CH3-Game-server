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

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| player | 없음 | 로그인 세션의 Django Player 객체; pk를 subject_id로 변환. |
| slot_id | 없음 | village-board 또는 lobby-banner. |

반환·실패: 공개 dict 또는 ad:null; ValueError(invalid_slot)/AdsUnavailable.

의사코드: 슬롯/서버 키 검사 → 로그인 Player subject와 두 헤더 POST → read 65537 뒤 65536 bytes 상한·슬롯/금액/소재/공개 문자열 검증 → 공개 선택 정규화. 이 함수는 call_ads를 호출하지 않으며 이번 작업에서 기존 본문을 보존했다.

직접 호출: `AdsUnavailable`, `Request`, `ValueError`, `any`, `data.get`, `isinstance`, `json.dumps`, `json.dumps({'media_id': media_id, 'subject': {'media_id': media_id, 'subject_id': str(player.pk)}, 'slot_id': slot_id, 'context': {}}).encode`, `json.loads`, `len`, `response.read`, `result.values`, `str`, `type`, `urlopen`.

## `request_ad_event(player, decision_id, event_type)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| player | 없음 | 로그인 세션의 Django Player 객체; pk를 subject_id로 변환. |
| decision_id | 없음 | 선택 결정 ID 문자열; 이벤트 중계는1..128자. |
| event_type | 없음 | impression 또는 click 문자열. |

반환: event_id·event_type·created 세 필드만 있는 dict. created의 True/False 모두 허용한다. 입력/거절은 ValueError, 빈 서버 키는 AdsUnavailable(media_key_missing), status 503은 AdsUnavailable(ads_unavailable), 잘못된 200 본문은 AdsUnavailable(invalid_ad_event_response)다.

의사코드: 서버 키 검사 → ID 1..128자·종류 검사 → 설정의 매체 ID와 str(player.pk)로 payload 구성 → call_ads로 /api/media/events/ 호출 → 503 구별 → 200 외에는 사전 여부 확인 후 허용 오류만 ValueError로 전달 → 200은 사전·동일 사건 ID·동일 종류·created bool 검사 → 공개 세 필드 반환.

직접 호출: `call_ads`, `AdsUnavailable`, `ValueError`, `data.get`, `isinstance`, `len`, `str`, `type`. call_ads는 상태와 JSON 두 값을 반환한다. 허용 오류는 decision_snapshot_missing·decision_not_found_for_subject·impression_required·decision_id_required·event_type_invalid이며 그 외는 ad_event_rejected다. 로그인 Player 조회와 HTTP 응답 변환은 호출하는 ad_views.ad_event의 책임이다.

## 상태·값 출처

CREATIVE_PATHS는 빈 문자열·/static/ads/creatives/forest-tools.png·/static/ads/creatives/camp-tea.png의 frozenset이다. ADS_BASE_URL·ADS_MEDIA_ID·ADS_MEDIA_KEY는 기존 서버 설정에서 읽는다. request/payload/status/data와 allowed 집합은 해당 함수가 생성·소유한다. subject_id의 출처는 로그인 Player.pk, decision_id와 event_type의 출처는 호출자의 검증된 사건 입력이다. 이 계층은 snapshot이나 사건을 DB에 쓰지 않는다. 비밀값·쿠키·CSRF 토큰은 문서/증거에 복사하지 않는다.
