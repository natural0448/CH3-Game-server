# server/game/static/game/ad_preview.js

#request-ad click은 선택 슬롯을 고정하고 nextRequestAt Map(초기 비어 있음)에서 슬롯별15s 간격을 검사한다. 같은 origin session/CSRF GET 후 JSON POST. 허용PNG를 Image.decode 성공 후 제목/본문/decision ID/금액과 함께 표시한다. 없음은 card hidden, 실패는 별도 message. 키·사건 저장·노출 수치를 다루지 않는다.
