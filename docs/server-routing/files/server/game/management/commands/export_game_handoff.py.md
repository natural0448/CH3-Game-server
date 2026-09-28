# `server/game/management/commands/export_game_handoff.py`

## 책임과 호출 경계

MySQL의 `GameEvent` 확정 사실을 event time 순서로 읽어 Lake 인계용 UTF-8 JSON Lines 파일로 원자적으로 교체한다. Kafka를 조회하거나 partition·offset을 만들어 넣지 않으며, 게임 상태를 다시 적용하지 않는다.

## 클래스와 메서드

### `Command.add_arguments(self, parser)`

- `parser`: Django가 전달한 명령행 parser.
- `--output`: 필수 출력 파일 경로.
- `--since`: 선택 시작 시각. timezone을 포함한 ISO 문자열이며 포함 경계다.
- `--until`: 선택 종료 시각. timezone을 포함한 ISO 문자열이며 제외 경계다.

```text
output 필수 인자 등록
since와 until 선택 인자 등록
```

직접 호출: Django management command argument parser의 `add_argument`.

### `Command.handle(self, *args, **options)`

- `args`: Django 관리명령 위치 인자. 이 명령에서는 사용하지 않는다.
- `options`: output, since, until을 포함한 Django 명령 옵션.

```text
GameEvent를 event_time, event_id 오름차순으로 조회
since가 있으면 timezone 포함 ISO 시각으로 변환하고 event_time >= since 적용
until이 있으면 timezone 포함 ISO 시각으로 변환하고 event_time < until 적용
출력 부모 폴더 생성
같은 경로의 .tmp 파일을 UTF-8로 열기
query를 1000행 단위 iterator로 읽기
각 행에서 schema_version,event_id,event_type,player_id,room_id,event_time,payload 구성
한 줄에 JSON 객체 하나씩 기록
완성된 임시 파일을 최종 output으로 교체
내보낸 사건 수와 출력 경로 표시
```

직접 호출: `GameEvent.objects.order_by/filter/iterator`, `datetime.fromisoformat`, `Path.mkdir/open/replace`, `json.dumps`, Django `CommandError`와 `self.stdout.write`.

## 주요 값과 출처

- `query`: `GameEvent` DB 행을 `event_time`, `event_id`로 정렬한 QuerySet이며 선택 시각 경계가 적용된다.
- `output`: 사용자가 `--output`으로 준 경로의 절대경로.
- `temporary`: output suffix 뒤에 `.tmp`를 붙인 원자적 작성 경로.
- `row`: DB 확정 사실에서 가져온 schema version 1 JSON 객체. `event_time`은 UTC ISO 문자열이고 `payload`는 저장된 JSON 객체다.
- `count`: 실제 파일에 기록한 확정 사실 행 수.
