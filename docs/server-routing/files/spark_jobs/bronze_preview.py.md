# spark_jobs/bronze_preview.py

## 책임과 호출 계층

기존 Spark 클러스터에서 Bronze NDJSON의 전달 위치와 partition별 행 수·서로 다른 key 수·offset 범위를 읽는다. Kafka나 Django API를 호출하지 않는다. 실행 경로는 19일차 7교시의 `spark_jobs/bronze_preview.py`다.

## 입력과 변수

- `p`: `argparse.ArgumentParser()`; 필수 문자열 `--input`은 읽을 NDJSON 경로다.
- `args`: `p.parse_args()` 결과. `args.input`을 Spark JSON reader에 전달한다.
- `spark`: `SparkSession.builder.appName("village-bronze-preview").getOrCreate()` 결과. Master는 제출 환경에서 정한다.
- `schema`: nullable `topic/key/value` 문자열, `partition` 정수, `offset` long 필드의 `StructType`.
- `raw`: `spark.read.schema(schema).json(args.input)`의 DataFrame. 원본을 수정하지 않는다.

## 실행 의사코드와 직접 호출

```text
argparse로 --input을 읽는다
SparkSession을 얻고 명시적 스키마로 JSON 파일을 읽는다
select(topic, partition, offset).show(5, truncate=False)
groupBy(partition).agg(count(*), countDistinct(key), min(offset), max(offset))
    .orderBy(partition).show(truncate=False)
spark.sparkContext.master를 출력한다
spark.stop()으로 이 작업의 세션을 종료한다
```

직접 호출하는 외부 코드는 argparse와 PySpark의 Session·schema·DataFrame·집계 API다. 출력은 콘솔 표이며 반환값·클래스·함수 정의는 없다.

## 출력 계약

첫 표는 최대 5행의 `topic/partition/offset` 미리보기이며 정렬된 최신 사건 목록이 아니다. 두 번째 표는 `partition`, `rows`, `distinct_keys`, `first_offset`, `last_offset`이다. `countDistinct("key")`는 null을 제외하며 접속자 수·고유 event_id 수를 계산하지 않는다. `master =` 출력은 실제 SparkContext의 Master 주소다. 전체 원문을 driver의 Python 리스트로 수집하지 않는다.
