# server/analytics/lake_views.py

## 책임과 직접 호출

`@login_required` 뷰 `lake_status(request)`는 게시된 보존 검사 JSON만 읽어 응답한다. request는 Django HttpRequest이고 반환값은 JsonResponse 또는 미로그인 redirect다. 검사·복사·Spark 작업을 실행하지 않는다.

## 변수·입력·의사코드

- `path=Path(settings.BASE_DIR).parent / "data" / "marts" / "lake-status.json"`.
- `data`: path.read_text(encoding="utf-8")를 json.loads한 게시 사전.

```text
login_required가 인증을 확인한다
path가 없으면 schema_version=1/status=pending/message를 HTTP 200으로 반환
파일 읽기 또는 JSON 오류이면 status=unavailable/message를 HTTP 503으로 반환
정상이면 schema_version/status=ready/dataset_id/dataset_version/captured_at/
generated_at/rows/bytes/matched/verification_scope만 JsonResponse로 반환
```

직접 호출은 Path.exists/read_text, json.loads, JsonResponse, login_required다. 원본 event 배열·player 목록·인증 정보를 응답에 복사하지 않는다. 게시 데이터의 필수 필드가 빠지면 현재 구현은 KeyError를 처리하지 않는다.
