# server/game/ad_views.py

## 22일차 이미지 광고 최종 반영

ad_preview는 login_required GET HTML이다. ad_decision은 CSRF를 유지한 POST JSON으로 미인증401, invalidJSON/slot400, Player없음404, gateway실패503, 선택성공200을 반환한다. Player는 request.user의 OneToOne 조회 결과만 사용하고 클라이언트 player_id/subject는 신뢰하지 않는다.

### `ad_preview(request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: HTML HttpResponse 또는 미로그인302/메서드405.

의사코드: Django 로그인/GET 검사 → preview template.

직접 호출: `render`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `ad_decision(request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: JsonResponse 200/400/401/404/503, CSRF403, 다른 메서드405.

의사코드: POST/CSRF → 로그인 → JSON·slot → request.user의 Player → gateway 호출 → 성공/503 JSON.

직접 호출: `Player.objects.filter(user=request.user).first`, `JsonResponse`, `json.loads`, `isinstance`, `payload.get`, `Player.objects.filter`, `request_decision`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
