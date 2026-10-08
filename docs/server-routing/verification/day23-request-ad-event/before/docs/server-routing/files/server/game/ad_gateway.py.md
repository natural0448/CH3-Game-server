# server/game/ad_gateway.py

기존 서버 설정 ADS_BASE_URL·ADS_MEDIA_ID·ADS_MEDIA_KEY를 읽는다. 실제 키는 응답/접속기에 전달하지 않는다. decision과event 모두 X-Media-ID/X-Media-Key를 붙이고 Player.pk를 공개 subject_id 문자열로 사용한다. 요청 timeout3초, 성공 JSON read65537 뒤64KiB 상한. CREATIVE_PATHS는 빈 문자열과 /static/ads/creatives/forest-tools.png, camp-tea.png만 허용한다. 이벤트 오류는 교안의 허용 코드만 전달하고 나머지는 ad_event_rejected,503/네트워크/부정한 receipt는 AdsUnavailable이다. 현재 별도 request 함수 구조를 유지하여 call_ads 파일을 새로 만들지 않았다.

직접 호출의 기대 계약: get_db는 기존 Database, find_one은 dict/None, find·sort·limit는 Cursor, update_one은 UpdateResult, insert_one은 InsertOneResult, create_index는 색인 이름이다. Django render/JsonResponse는 HttpResponse, JSON parse는 dict 등 JSON 값, urlopen은 응답 stream, patch/assert는 테스트 fixture/검증을 제공한다. 하위 계층 내부는 해당 짝 문서에 있다.

## `class AdsUnavailable(Exception)`

기반 클래스: Exception. 메서드와 상태는 아래 계약을 따른다.

## `request_decision(player, slot_id)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| player | 없음 | 로그인 세션의 Django Player 객체; pk를 subject_id로 변환. |
| slot_id | 없음 | village-board 또는 lobby-banner. |

반환·실패: 공개 dict 또는 ad:null; ValueError(invalid_slot)/AdsUnavailable.

의사코드: 슬롯/서버 키 검사 → 로그인 Player subject와 두 헤더 POST → 크기/슬롯/금액/소재/공개 문자열 검증 → 공개 선택 정규화.

직접 호출: `AdsUnavailable`, `Request`, `ValueError`, `any`, `data.get`, `isinstance`, `json.dumps`, `json.dumps({'media_id': media_id, 'subject': {'media_id': media_id, 'subject_id': str(player.pk)}, 'slot_id': slot_id, 'context': {}}).encode`, `json.loads`, `len`, `response.read`, `result.values`, `str`, `type`, `urlopen`.

## `request_ad_event(player, decision_id, event_type)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| player | 없음 | 로그인 세션의 Django Player 객체; pk를 subject_id로 변환. |
| decision_id | 없음 | 선택 결정 ID 문자열; 이벤트 중계는1..128자. |
| event_type | 없음 | impression 또는 click 문자열. |

반환·실패: receipt dict; 입력/거절ValueError 또는 AdsUnavailable.

의사코드: ID1..128자·종류/키 검사 → Player subject 두 헤더 POST → 크기/receipt상관관계/created bool 검사 → 허용 공개필드; HTTPError는 허용 오류 코드만 전달.

직접 호출: `AdsUnavailable`, `Request`, `ValueError`, `body.get`, `data.get`, `error.split`, `exc.read`, `isinstance`, `json.dumps`, `json.dumps({'media_id': media_id, 'subject': {'media_id': media_id, 'subject_id': str(player.pk)}, 'decision_id': decision_id, 'event_type': event_type}).encode`, `json.loads`, `len`, `response.read`, `str`, `type`, `urlopen`.

## 상태·값 출처

지역 변수는 해당 함수가 소유하며 request/입력·서버 설정·DB 조회 또는 위 의사코드의 생성 단계에서 얻는다. 저장 snapshot과 receipt의 쓰기는 서비스/사건 계층이 맡는다. 테스트 연결·patch·가짜 응답은 해당 테스트 클래스만 소유하고 정리한다. 비밀값·쿠키·CSRF 토큰은 문서/증거에 복사하지 않는다.
