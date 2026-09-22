# `server/game/management/commands/inspect_game_facts.py`

## 책임과 공개 범위

최근 확정 게임 사실을 작은 수로 읽어 식별자 관계를 확인하는 읽기 전용 Django 관리 명령이다. 게임 상태와 `GameEvent`를 쓰지 않으며 인증·세션·사용자 비밀번호를 출력하지 않는다.

## 클래스와 메서드

### `Command.add_arguments(self, parser) -> None`

파라미터:

- `parser`: Django 관리 명령 argument parser.

의사코드:

```text
--rows 정수 인자를 등록한다
허용 값은 3, 5, 10이고 기본값은 5다
```

직접 호출: Django argument parser의 `add_argument`.

### `Command.handle(self, *args, **options) -> None`

파라미터:

- `args`: Django가 전달하는 추가 위치 인자.
- `options["rows"]`: DB에서 가져올 최근 행 상한. `3`, `5`, `10` 중 하나.

의사코드:

```text
GameEvent를 event_time 내림차순, event_id 내림차순으로 정렬한다
QuerySet을 rows만큼 slice하여 DB 조회량을 제한한다
각 행에서 event_id, payload.command_id, player_id, event_type, room_id, event_time을 고른다
published_at을 ISO 시각 또는 null로 표시한다
payload의 키 이름만 정렬하고 transition 객체 존재 여부를 bool로 표시한다
각 공개 사전을 한 줄 JSON으로 표준 출력한다
```

직접 호출:

- `GameEvent.objects.order_by`: 최근 확정 사실을 결정적으로 읽는다.
- `event.payload.get`: JSON payload 안의 command ID를 읽는다.
- `json.dumps`: 공개 projection을 UTF-8로 읽기 쉬운 JSON 문자열로 만든다.
- `self.stdout.write`: 한 사실을 한 줄씩 출력한다.

## 변수·상수

- `help`: 명령의 제한된 공개 조회 목적과 게임 상태를 변경하지 않는다는 설명.
- `events`: 전체 목록으로 만들지 않은 제한된 `QuerySet`.
- `row`: 식별자·사건 시각·전달 시각과 payload 구조 요약만 갖는 임시 사전. payload 값 전체는 출력하지 않는다.
