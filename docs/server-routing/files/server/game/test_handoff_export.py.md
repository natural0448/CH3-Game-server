# `server/game/test_handoff_export.py`

## 책임

Lake 인계 관리명령이 확정 사실을 순서가 있는 UTF-8 JSONL로 내보내고, 반개구간 시각 경계와 DB 원천 계약을 지키는지 검사한다.

## 클래스와 메서드

### `ExportGameHandoffTests.setUp(self)`

테스트 user와 `room-handoff` Player를 만들고, 서로 다른 시각·payload·UUID를 가진 이동과 채집 확정 사실 두 건을 DB에 준비한다.

### `ExportGameHandoffTests.export(self, directory, **options)`

- `directory`: 임시 JSONL을 쓸 부모 폴더.
- `options`: 선택적인 since·until 명령 옵션.
- 반환값: output `Path`, 파싱한 JSON 행 목록, 명령 표준 출력 문자열.

```text
임시 폴더 아래 game-events.jsonl 경로 구성
call_command로 export_game_handoff 실행
UTF-8 JSONL의 비어 있지 않은 각 줄을 json.loads
경로, 행 목록, stdout 반환
```

### `ExportGameHandoffTests.test_exports_ordered_json_lines_without_invented_kafka_positions(self)`

```text
전체 두 사건 내보내기
임시 파일이 남지 않고 event_time 순서인지 확인
필드 집합과 payload command_id, UTC event_time 확인
DB export에 Kafka partition/offset이 없는지 확인
출력 사건 수가 2인지 확인
```

### `ExportGameHandoffTests.test_since_is_inclusive_until_is_exclusive_and_timezone_is_required(self)`

```text
두 번째 사건 시각을 since 포함 경계로 지정
그 다음 분을 until 제외 경계로 지정
두 번째 사건만 내보냈는지 확인
timezone 없는 since가 CommandError인지 확인
```

직접 호출: Django `get_user_model`, `call_command`, `TestCase`, `GameEvent`, `Player`, `TemporaryDirectory`, `json.loads`.
