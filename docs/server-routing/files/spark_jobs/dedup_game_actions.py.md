# spark_jobs/dedup_game_actions.py

## 책임과 입력·변수

행동 중복 제거. CLI --input/--output 필수. business는 schema_version,event_id,event_type,player_id,room_id,event_time,payload. 전달 위치는 hash 제외.

## 호출·의사코드

모듈 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다.

```text
payload map_entries 정렬 → struct JSON SHA-256 body_hash → event_id별 variants>1이면 중단 → Window(event_id), topic/partition/offset 첫 행 선택 → rn/body_hash/reason/value 제거 → accepted/logical/duplicate_deliveries 출력 → Parquet errorifexists 저장 → stop.
```

직접 호출은 위 흐름에 명시한 Python 표준 라이브러리와 Spark API이며 하위 계층 내부는 설명하지 않는다. 반환값은 없고 출력·게시 파일 또는 표가 결과다.
