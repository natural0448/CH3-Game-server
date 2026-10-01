# spark_jobs/add_game_date.py

## 책임과 입력·변수

한국 날짜 추가. CLI --input/--output 필수. p는 parsed_time(UTC timestamp)과 event_time(원문 문자열)을 가진 기본 Silver. 세션 UTC, 달력 시간대 Asia/Seoul.

## 직접 호출·의사코드

모듈/스크립트 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다. 파라미터 기본값·허용 범위는 위 입력 항목과 같다. 반환값은 없고 결과는 출력·Parquet·JSON 또는 셸 변수다. 각 중간 변수는 현재 파일이 소유한다.

```text
dated <- p.withColumn(event_date,to_date(from_utc_timestamp(parsed_time,Asia/Seoul)))
원문 event_time과 UTC parsed_time은 그대로 유지
시각·날짜 show → event_date partition Parquet errorifexists 저장
boundary 14:59:59Z / 15:00:00Z / 00:00:00Z의 날짜 show → stop
```

직접 호출은 위에 명시한 SparkSession/DataFrame 함수, Python 표준 json/Path/datetime/os 또는 실행 명령이다. Spark API 결과는 다음 단계의 표나 실제 건수이며 네트워크·게임 규칙의 내부 구현을 설명하지 않는다.
