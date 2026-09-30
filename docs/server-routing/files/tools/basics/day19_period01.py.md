# tools/basics/day19_period01.py

## 책임과 호출 계층

1교시 방 수 계산 연습이다. 현재 파일은 고정 summary 대신 실제 게시 summary를 읽는 사용자의 입력 방식을 유지한다. 서버·Spark는 호출하지 않는다.

## 변수와 출처

- `root=Path("data")`, `summary_path=root / "marts" / "game-summary.json"`.
- `summary`: summary_path의 UTF-8 JSON; `event_count/by_room` 필드를 읽는다.
- `room_count=len(summary["by_room"])`: 실제 입력의 방별 집계 행 수.
- `result`: schema_version=1; serving은 path/event_count/room_count/rebuildable=True. source의 topic=game.actions.v1, identity=event_id, position=[topic,partition,offset], purpose=rebuild daily statistics. state_owner=MySQL game_player.
- `out=root / "contracts" / "lake-inventory_basic.json"`: 사용자의 기존 연습 결과 저장 경로.

## 실행 의사코드와 직접 호출

```text
Path.read_text와 json.loads로 실제 summary를 읽는다
len(by_room)을 room_count에 넣는다
result를 조립하고 부모 폴더를 만든다
result를 UTF-8 JSON으로 저장하고 기존 JSON 출력도 유지한다
print("room_count", room_count)를 추가 출력한다
```

직접 호출: pathlib의 읽기·폴더 생성·쓰기, json.loads/dumps, len, print. 정의한 클래스·함수·메서드·CLI 인자·반환값은 없다. 고정 예제의 2와 실제 입력의 방 수는 같을 필요가 없다.
