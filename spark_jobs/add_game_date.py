import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# UTC 세션에서 중복 제거된 입력을 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
p = spark.read.parquet(args.input)

# 한국 달력 날짜를 계산하고 날짜별 새 Parquet 경로에 저장한다.

dated = p.withColumn(
    "event_date", F.to_date(F.from_utc_timestamp("parsed_time", "Asia/Seoul"))
)
dated.select("event_time", "parsed_time", "event_date").show(10, truncate=False)
dated.write.mode("errorifexists").partitionBy("event_date").parquet(args.output)

# 한국 자정 직전·직후의 UTC 시각으로 날짜 경계를 확인한다.
boundary = spark.createDataFrame([
    ("2026-09-11T14:59:59Z",),
    ("2026-09-11T15:00:00Z",),
    ("2026-09-11T00:00:00Z",),  # 추가
], ["text_time"])
boundary.select(
    "text_time",
    F.to_date(F.from_utc_timestamp(F.col("text_time"), "Asia/Seoul")).alias("date")
).show(truncate=False)
spark.stop()
