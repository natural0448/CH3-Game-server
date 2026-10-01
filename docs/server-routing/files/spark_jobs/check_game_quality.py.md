# spark_jobs/check_game_quality.py

## 책임과 입력·변수

품질 검사. CLI --input/--output 필수. p=입력 Parquet. checked는 원문 event_time을 유지하고 parsed_time을 try_to_timestamp로 만든 표. reason은 첫 오류 사유 또는 accepted.

## 호출·의사코드

모듈 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다.

```text
UTC 세션 생성 → missing/schema/event/room/time/action 조건 검사 → reason별 count → accepted의 room별 count → reason을 유지한 accepted 및 나머지 quarantine을 각각 errorifexists 저장 → stop.
```

직접 호출은 위 흐름에 명시한 Python 표준 라이브러리와 Spark API이며 하위 계층 내부는 설명하지 않는다. 반환값은 없고 출력·게시 파일 또는 표가 결과다.
