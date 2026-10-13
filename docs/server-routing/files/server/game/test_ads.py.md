# server/game/test_ads.py

격리 memory SQLite와 모의 HTTP 응답에서 게임 로그인·CSRF·Player·이미지 whitelist·공개 receipt·empty를 검사한다. 수정 교안의 두 헤더, 허용 오류 전달, 추가 본문 필드 거부, no-store, Player 없음409를 검증한다. 실제 MySQL·광고 DB·유저 키는 사용하지 않는다.

사건 성공 응답 fixture는 BytesIO stream에 status=200을 붙인다. call_ads가 실제 HTTP 응답처럼 status와 JSON 본문을 함께 읽도록 하는 테스트 적응이며 기존 assertion과 검사 범위는 유지한다.

직접 호출의 기대 계약: get_db는 기존 Database, find_one은 dict/None, find·sort·limit는 Cursor, update_one은 UpdateResult, insert_one은 InsertOneResult, create_index는 색인 이름이다. Django render/JsonResponse는 HttpResponse, JSON parse는 dict 등 JSON 값, urlopen은 응답 stream, patch/assert는 테스트 fixture/검증을 제공한다. 하위 계층 내부는 해당 짝 문서에 있다.

## `selection()`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| 없음 | — | 인자 없음 |

반환: 공개 광고 선택 예시 dict. decision_id=decision-test, campaign_id=forest-tools, slot_id=village-board, policy_version=highest-bid/v1, bid_units=30, creative_path=/static/ads/creatives/forest-tools.png와 title/body를 포함한다. 인자는 없으며 DB나 실제 서버를 호출하지 않는다.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: .

## `class GatewayTests(SimpleTestCase)`

기반 클래스: SimpleTestCase. 메서드와 상태는 아래 계약을 따른다.

## `GatewayTests.test_event_error_codes_are_preserved_without_private_details(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `HTTPError`, `SimpleNamespace`, `io.BytesIO`, `json.dumps`, `json.dumps({'error': code + ': private detail'}).encode`, `patch`, `request_ad_event`, `self.assertRaises`, `self.assertRaisesRegex`, `self.subTest`.

## `GatewayTests.test_event_public_receipt_duplicate_and_recipient(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `SimpleNamespace`, `io.BytesIO`, `json.dumps`, `json.dumps(receipt).encode`, `json.dumps({**receipt, **changes}).encode`, `json.loads`, `opened.call_args.args[0].get_header`, `patch`, `request_ad_event`, `self.assertEqual`, `self.assertRaises`, `self.subTest`.

## `GatewayTests.test_public_player_identity_and_legacy_amount_are_adapted(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `SimpleNamespace`, `io.BytesIO`, `json.dumps`, `json.dumps(payload).encode`, `json.loads`, `patch`, `request_decision`, `selection`, `self.assertEqual`, `self.assertNotIn`.

## `GatewayTests.test_empty_and_invalid_response_or_missing_key(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `SimpleNamespace`, `io.BytesIO`, `json.dumps`, `json.dumps({**selection(), **changes}).encode`, `override_settings`, `patch`, `request_decision`, `selection`, `self.assertEqual`, `self.assertRaises`, `self.subTest`.

## `class RelayTests(TestCase)`

기반 클래스: TestCase. 메서드와 상태는 아래 계약을 따른다.

## `RelayTests.test_event_session_csrf_and_spoofed_recipient(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `Client`, `client.force_login`, `client.get`, `client.get('/api/auth/csrf/').json`, `client.post`, `event.assert_not_called`, `json.dumps`, `patch`, `response.json`, `self.assertEqual`, `self.client.post`.

## `RelayTests.test_event_bad_input_and_outage(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `AdsUnavailable`, `patch`, `self.assertEqual`, `self.client.force_login`, `self.client.post`.

## `RelayTests.test_event_snapshot_error_and_missing_player_status(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `ValueError`, `patch`, `response.json`, `self.assertEqual`, `self.client.force_login`, `self.client.post`, `self.player.delete`.

## `RelayTests.setUp(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; fixture 실패는 테스트 실패로 보고.

의사코드: 자기 테스트 클래스/메서드 fixture 준비·patch 또는 연결/UUID DB 정리. 실제 수업 DB를 사용하지 않는다..

직접 호출: `Player.objects.create`, `get_user_model`, `get_user_model().objects.create_user`.

## `RelayTests.test_login_post_only_and_current_player_ignore_spoofed_subject(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `json.dumps`, `patch`, `selection`, `self.assertEqual`, `self.client.force_login`, `self.client.get`, `self.client.post`.

## `RelayTests.test_csrf_is_required_for_game_relay(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `Client`, `client.force_login`, `client.get`, `client.get('/api/auth/csrf/').json`, `client.post`, `json.dumps`, `patch`, `selection`, `self.assertEqual`.

## `RelayTests.test_invalid_input_outage_and_preview(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 인스턴스. 상태 쓰기는 해당 객체가 소유한다. |

반환·실패: None; 테스트 실패 AssertionError.

의사코드: 이름에 해당하는 fixture 준비 → 실제 함수/HTTP 호출 → 반환·상태·저장 불변식 assert → fixture 정리.

직접 호출: `AdsUnavailable`, `patch`, `self.assertContains`, `self.assertEqual`, `self.client.force_login`, `self.client.get`, `self.client.post`, `self.subTest`.

## 상태·값 출처

지역 변수는 해당 함수가 소유하며 request/입력·서버 설정·DB 조회 또는 위 의사코드의 생성 단계에서 얻는다. 저장 snapshot과 receipt의 쓰기는 서비스/사건 계층이 맡는다. 테스트 연결·patch·가짜 응답은 해당 테스트 클래스만 소유하고 정리한다. 비밀값·쿠키·CSRF 토큰은 문서/증거에 복사하지 않는다.


## class PlayerContextTests(SimpleTestCase)

25일차 context 검사를 기존 test_ads.py에 추가했다. 실제 User/Player/광고 DB를 만들지 않고 RequestFactory·Player 조회 mock·BytesIO HTTP fixture를 사용한다. 기존 GatewayTests/RelayTests 본문은 보존했다. 모든 test 메서드는 기본값 없는 self, 정상 반환 None, 실패 AssertionError 계약이다. 고정 ADS 설정·ID 12·다섯 공개 필드는 synthetic fixture이고 실제 키/세션은 사용하지 않는다.

### PlayerContextTests.setUp(self)

self는 기본값 없는 테스트 인스턴스다. 반환 None. 의사코드: RequestFactory → pk 12 Player namespace → 공개 context fixture를 self에 보관. 직접 호출은 RequestFactory와 SimpleNamespace다. 각 테스트 인스턴스가 fixture를 소유한다.

### PlayerContextTests.test_logged_in_player_ignores_query_recipient_and_does_not_cache(self)

의사코드: resolver가 views.ad_context인지 확인 → subject_id=9999 요청에도 로그인 user로 Player 조회 → pk 12 gateway 조회 → subject 12·200·no-store 확인. 직접 호출은 resolve, factory.get, patch, ad_context, json.loads와 assert다.

### PlayerContextTests.test_login_missing_player_and_outage_have_separate_statuses(self)

의사코드: 비로그인 401/ORM 미호출 → Player 없음404 → gateway 장애503 공개 오류 → POST405. 직접 호출은 ad_context, factory.get/post, patch, AdsUnavailable fixture, json.loads와 assert다.

### PlayerContextTests.test_context_is_fetched_before_selection_and_passed_as_snapshot(self)

의사코드: context 응답/선택 응답 두 BytesIO → request_decision → 호출 순서·URL·subject-only 본문·선택 context·body/image/금액·두 timeout 검사. 직접 호출은 io.BytesIO, json.dumps/loads, patch, request_decision, Request.get_header와 assert다. DB 결정 기록은 만들지 않는다.

### PlayerContextTests.test_response_recipient_types_and_timezone_are_validated(self)

의사코드: 다른 대상·bool version·naive 시각·추가 필드 응답은 AdsUnavailable → 빈 정상 context는 {}. 직접 호출은 BytesIO, JSON, patch, request_context, subTest/assertRaises/assertEqual이다. 응답 검증과 빈 복사본 정상 상태를 구별한다.
