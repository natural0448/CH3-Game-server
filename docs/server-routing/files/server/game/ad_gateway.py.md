# server/game/ad_gateway.py

## 22일차 이미지 광고 최종 반영

게임 서버만 매체 API를 호출한다. request_decision은 Player.pk를 문자열 subject_id로 변환하고 MEDIA_ID, 빈 context, 슬롯으로 JSON을 만든다. 서버 env 키는 X-Media-Key header로만 사용한다. timeout3s, 응답64KiB 이하, amount 정수1..10000, 제목80/본문300, 허용 PNG2개 또는 빈 경로를 검사한다. 공개 필드만 return하고 광고주 소유자/헤더는 버린다. empty/ad:null은 ad:null로 통일, 오류는 AdsUnavailable. CREATIVE_PATHS=frozenset(blank, forest-tools path, camp-tea path).

클래스 계약: `class AdsUnavailable(Exception)`.


### `request_decision(player, slot_id)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| player | 없음 | Django Player 객체; pk가 수신자 식별자. |
| slot_id | 없음 | village-board 또는 lobby-banner. |

반환·실패: public dict 또는 AdsUnavailable/invalid slot ValueError.

의사코드: slot/env key 검사 → Player.pk subject JSON → media header POST → 크기/공개 타입/소재 검증 → 정규화.

직접 호출: `Request`, `ValueError`, `AdsUnavailable`, `json.loads`, `data.get`, `any`, `json.dumps({'media_id': media_id, 'subject': {'media_id': media_id, 'subject_id': str(player.pk)}, 'slot_id': slot_id, 'context': {}}).encode`, `urlopen`, `response.read`, `len`, `isinstance`, `type`, `json.dumps`, `result.values`, `str`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
