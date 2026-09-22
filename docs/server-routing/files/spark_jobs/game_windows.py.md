# `spark_jobs/game_windows.py`

## 책임과 호출 위치

`game.actions.v1`의 전달 레코드를 Spark Structured Streaming으로 읽고 서버 `event_time` 기준 10초 tumbling 또는 20초 sliding 창을 계산해 Parquet에 append한다. 게임 상태를 판정하거나 변경하지 않으며, 기존 원천 수집 checkpoint와 진행 위치를 공유하지 않는다.

호출 계층은 `server/analytics/management/commands/run_game_windows.py`다. 해당 관리 명령이 Spark 연결 주소와 데이터 루트를 인자로 전달한다.

## 상수

```text
ACTION_TYPES
  값: player.moved, player.gathered, player.trained.
  출처: Python 행동 변환기가 game.actions.v1에 보내는 분석 대상 행동 계약.

EVENT_SCHEMA
  공통 봉투의 schema_version, event_id, event_type, player_id, room_id,
  event_time과 payload의 command_id·좌표·coins·version·action_label을 읽는다.
  계산에 꺼내지 않은 전체 원문은 raw_value가 보존한다.

SHUFFLE_PARTITIONS
  값: 4.
  출처: 현재 단일 Spark Worker가 제공하는 core 수와 같은 병렬 집계 partition 수.
```

## 함수

### `parse_args() -> argparse.Namespace`

```text
--data-dir 필수 경로 등록
--bootstrap-servers 필수 Kafka 주소 등록
--topic 기본값 game.actions.v1 등록
--kind tumbling|sliding, 기본값 tumbling 등록
파싱 결과 반환
```

### `read_actions(spark, bootstrap_servers, topic, kind) -> DataFrame`

- `spark`: 생성된 `SparkSession`.
- `bootstrap_servers`: 관리 명령이 settings에서 전달한 Kafka 주소 문자열.
- `topic`: 읽을 분석 Topic. 기본 호출 값은 `game.actions.v1`.
- `kind`: Kafka consumer group 접두사를 분리하는 `tumbling` 또는 `sliding`.

```text
Kafka readStream을 earliest 시작 정책으로 구성
groupIdPrefix를 village-game-windows-<kind>로 분리
value 전체를 raw_value string으로 보존
topic·partition·offset과 EVENT_SCHEMA 해석 결과 선택
event_time을 timestamp로 변환
시각·event_id·schema_version 1·허용 행동 조건을 만족한 행만 반환
```

직접 호출하는 외부 코드는 Spark Kafka source, `from_json`, `to_timestamp`, DataFrame `select`와 `filter`다.

### `build_windows(actions, kind) -> DataFrame`

- `actions`: `read_actions`가 반환한 streaming DataFrame.
- `kind`: 명령행에서 검증된 `tumbling` 또는 `sliding`.

```text
kind가 tumbling이면 duration=10 seconds, sliding이면 duration=20 seconds
event_time에 10초 watermark 적용
duration 길이·10초 이동 간격의 window와 event_type으로 groupBy
전달 레코드 수 count
실제 kind, window_start, window_end, event_type, count 컬럼 반환
```

직접 호출하는 외부 코드는 Spark `withWatermark`, `window`, `groupBy`, `count`, `select`다.

### `main() -> None`

```text
인자와 절대 data-dir 결정
kind별 app name과 Asia/Seoul 시간대·shuffle partition 4인 SparkSession 생성
read_actions 후 schema와 streaming 여부 출력
build_windows(actions, args.kind) 호출
data/lake/windows/<kind>에 Parquet append query 시작
data/checkpoints/windows/<kind>에 독립 checkpoint 기록
Windows Hadoop sink가 중첩 경로를 열기 전에 두 디렉터리를 명시적으로 생성
5초 processing trigger로 query 시작
awaitTermination(5) 동안 새 lastProgress batchId만 선택
공개 JSON 표현 전체를 같은 marts 폴더의 임시 파일에 먼저 기록
임시 파일을 progress-windows-<kind>.json으로 교체
터미널에는 kind·batchId·입력 행·eventTime·stateOperators만 출력
Ctrl+C 또는 종료 시 query와 SparkSession 정리
```

## 주요 변수와 경로

- `output`: `<data-dir>/lake/windows/<kind>`. 해당 창 종류의 확정 결과 Parquet.
- `checkpoint`: `<data-dir>/checkpoints/windows/<kind>`. 창 종류별 Kafka 진행 위치와 watermark 집계 상태.
- `progress_path`: `<data-dir>/marts/progress-windows-<kind>.json`. 해당 창 종류의 최근 완료 micro-batch 공개 JSON 스냅샷.
- `actions`: 원문과 Kafka 위치를 보존하고 event_time을 timestamp로 만든 streaming DataFrame.
- `final_windows`: `kind`, 창 시작·끝, 행동 종류, 전달 레코드 수를 가진 집계 DataFrame.
- `query`: `game-windows-<kind>` 이름의 append streaming query.
- `last_batch_id`: 동일한 완료 batch를 반복해서 파일에 쓰지 않기 위한 마지막 기록 ID. 게임 `event_id`가 아니다.
- `temporary`: 최종 progress 파일과 같은 폴더의 `.tmp` 경로. JSON 쓰기가 끝난 뒤 최종 파일을 대체한다.
- `SHUFFLE_PARTITIONS`: 값 4. Spark 상태 집계에 사용하는 shuffle partition 수다.
