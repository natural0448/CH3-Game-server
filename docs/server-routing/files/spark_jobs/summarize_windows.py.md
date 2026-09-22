# `spark_jobs/summarize_windows.py`

## 책임

확정되어 Parquet으로 게시된 tumbling·sliding 시간 창을 읽어 접속기가 조회할 `data/marts/windows.json` 스냅샷을 원자적으로 갱신한다. 실행 중인 Streaming Query나 Kafka에는 접근하지 않는다.

## 함수

### `main() -> None`

파라미터는 명령행에서 읽는다.

- `--data-dir`: `lake/windows/<kind>`를 읽고 `marts/windows.json`을 쓸 데이터 루트.
- `--rows`: 창 종류마다 가져올 최근 행 수. `5`, `10`, `20` 중 하나이며 기본값은 `20`이다.

의사코드:

```text
Asia/Seoul 시간대의 SparkSession을 만든다
각 kind(tumbling, sliding)에 대해
    Parquet 파일이 없으면 건너뛴다
    window_start 내림차순, event_type 오름차순으로 정렬한다
    --rows 개를 kind·시작·끝·event_type·count 형태로 수집한다
generated_at과 수집한 windows를 임시 JSON 파일에 쓴다
임시 파일을 data/marts/windows.json으로 교체한다
항상 SparkSession을 종료한다
```

직접 호출하는 외부 코드는 `pyspark.sql.SparkSession`, `pyspark.sql.functions`이다. 출력 시간은 `zoneinfo.ZoneInfo("Asia/Seoul")`에서 가져온다.

## 변수·상수

- `data_dir`: `--data-dir`을 절대 경로로 바꾼 값.
- `rows`: 두 종류의 확정 창을 담는 출력 배열.
- `source`: `<data-dir>/lake/windows/tumbling` 또는 `sliding`.
- `output`: `<data-dir>/marts/windows.json`.
- `temporary`: 출력 교체 전 사용하는 `<data-dir>/marts/windows.tmp`.

