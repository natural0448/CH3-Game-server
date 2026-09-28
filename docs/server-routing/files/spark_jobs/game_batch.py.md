# `spark_jobs/game_batch.py`

## 책임과 호출 경계

`--source raw|delta`에 따라 원본 JSONL 또는 고유 행동 Delta 테이블을 읽고 `event_id` 기준 행동·방별 집계를 `data/marts/game-summary.json`으로 게시한다.

Django 제출 계층에서 source와 데이터 루트를 전달받는다. 두 source의 payload 표현 차이를 집계에 사용하지 않고 공통 봉투 필드만 읽는다.

## 명령행 인자

```text
--data-dir
  필수. raw, lake, marts가 속한 데이터 루트.

--source
  raw 또는 delta. 기본값 raw.
```

## 최상위 실행 흐름

```text
명령행 인자와 절대 data-dir 결정
Asia/Seoul 시간대와 shuffle partition 2인 SparkSession 생성
source=delta이면 lake/silver/game_actions Delta 테이블 읽기
그 외에는 정의된 schema로 raw/game-events.jsonl 읽기
schema 출력
공통 식별자 미리보기 5행 출력
schema_version 1이고 event_id가 있는 행 선택
event_id 중복 제거
전체 전달 행·고유 사건·행동별·방별 수 계산
임시 JSON을 작성한 뒤 game-summary.json으로 교체
요약 출력 후 SparkSession 종료
```

직접 호출: Spark JSON reader, Delta reader, DataFrame filter/select/dropDuplicates/groupBy/count/collect, `Path.replace`.

## 주요 변수와 값 출처

- `schema`: raw JSONL의 공통 봉투와 `payload` 구조체 스키마.
- `records`: 선택한 source에서 읽은 DataFrame. Delta에서는 `payload_json`을 가진다.
- `actions`: `schema_version=1`과 유효한 `event_id`를 만족하고 `event_id` 중복을 제거한 DataFrame.
- `record_count`: source에서 읽은 전체 행 수.
- `event_count`: 고유 행동 수.
- `by_action`: `event_type`별 고유 행동 수.
- `by_room`: 상위 20개 `room_id`별 고유 행동 수.
- `temporary`: `<data-dir>/marts/game-summary.json.tmp`.
