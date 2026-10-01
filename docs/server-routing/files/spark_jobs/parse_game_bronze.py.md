# spark_jobs/parse_game_bronze.py

## 책임과 입력·변수

Bronze JSON 해석. CLI --input/--output은 필수. spark 시간대 UTC. outer는 topic/partition/offset/key/value, envelope는 schema_version/event_id/event_type/player_id/room_id/event_time/payload(map<string,string>).

## 호출·의사코드

모듈 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다.

```text
SparkSession 생성 → 원문 JSON 읽기 → from_json(value,envelope)를 event에 저장 → 전달 위치·value·event 필드 select → show → errorifexists Parquet 저장 → 다시 read/show → stop.
```

직접 호출은 위 흐름에 명시한 Python 표준 라이브러리와 Spark API이며 하위 계층 내부는 설명하지 않는다. 반환값은 없고 출력·게시 파일 또는 표가 결과다.
