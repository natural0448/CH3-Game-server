# tools/lake_inventory.py

## 책임과 호출 계층

게시된 게임 summary를 읽어 Lake의 재구성 원천과 현재 상태 저장소를 구분하는 현황 JSON을 만든다. Kafka·Spark·Django를 호출하지 않는다.

## 변수와 값의 출처

- `root=Path("data")`: 실행 작업 폴더 기준 data 경로.
- `summary_path=root / "marts" / "game-summary.json"`.
- `summary`: summary_path UTF-8 JSON을 json.loads한 사전. `event_count/by_room`을 읽는다.
- `room_count=len(summary["by_room"])`: 게시된 방별 집계 행 수. 현재 접속 방 수를 측정하지 않는다.
- `result`: schema_version=1. serving은 summary 경로·event_count·room_count·rebuildable=True, source는 topic=game.actions.v1·identity=event_id·position=[topic,partition,offset]·purpose=rebuild daily statistics, state_owner=MySQL game_player.
- `out=root / "contracts" / "lake-inventory.json"`: 현황 저장 경로.

## 실행 의사코드와 직접 호출

```text
Path.read_text와 json.loads로 summary를 읽는다
by_room의 길이를 room_count에 넣는다
result를 조립한다
out.parent.mkdir(parents=True, exist_ok=True)
json.dumps 결과를 out.write_text(encoding="utf-8")로 저장한다
같은 JSON을 print한다
```

외부 직접 호출은 pathlib의 읽기·폴더 생성·쓰기와 json.loads/dumps다. 정의한 함수·클래스·CLI 인자·반환값은 없다. rebuildable은 원본 보존을 전제로 한 설명이다.
