# server/game/test_ads.py

## 22일차 이미지 광고 최종 반영

GatewayTests는 subject/서버 header/공개 응답과 오류/빈값을, RelayTests는 인증·CSRF·payload ID 무시·Player없음·잘못된 슬롯/JSON·중계503·preview GET을 검증한다. 단위 테스트 mock urlopen만 사용하며 통합 fixture는 별도 검증 도구에 있다.

클래스 계약: `class GatewayTests(SimpleTestCase)`, `class RelayTests(TestCase)`.


### `selection()`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|

반환·실패: 코드 반환 식: `{'decision_id': 'decision-test', 'campaign_id': 'forest-tools', 'title': '숲 도구점', 'body': '도구', 'slot_id': 'village-board', 'policy_version': 'highest-bid/v1', 'bid_units': 30, 'creative_path': '/static/ads/creatives/forest-tools.png'}`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `GatewayTests.test_public_player_identity_and_legacy_amount_are_adapted(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `json.loads`, `self.assertEqual`, `self.assertNotIn`, `selection`, `patch`, `request_decision`, `SimpleNamespace`, `io.BytesIO`, `json.dumps(payload).encode`, `json.dumps`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `GatewayTests.test_empty_and_invalid_response_or_missing_key(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `patch`, `self.assertEqual`, `override_settings`, `self.assertRaises`, `request_decision`, `self.subTest`, `SimpleNamespace`, `io.BytesIO`, `json.dumps({**selection(), **changes}).encode`, `json.dumps`, `selection`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `RelayTests.setUp(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `get_user_model().objects.create_user`, `Player.objects.create`, `get_user_model`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `RelayTests.test_login_post_only_and_current_player_ignore_spoofed_subject(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `self.assertEqual`, `self.client.force_login`, `patch`, `self.client.post`, `self.client.get`, `selection`, `json.dumps`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `RelayTests.test_csrf_is_required_for_game_relay(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `Client`, `client.force_login`, `json.dumps`, `self.assertEqual`, `client.get('/api/auth/csrf/').json`, `patch`, `client.post`, `client.get`, `selection`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `RelayTests.test_invalid_input_outage_and_preview(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `self.client.force_login`, `self.assertContains`, `patch`, `self.assertEqual`, `self.client.get`, `self.subTest`, `AdsUnavailable`, `self.client.post`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
