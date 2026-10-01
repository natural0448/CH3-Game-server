import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입출력 경로를 받고 날짜가 붙은 Silver를 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
p.add_argument("--event-type", choices=["player.moved", "player.gathered", "player.trained"])
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
silver = spark.read.parquet(args.input)
if args.event_type:
    silver = silver.filter(F.col("event_type") == args.event_type)

# 날짜·방·행동 종류별 행동 수와 서로 다른 플레이어 수를 집계해 저장한다.
daily = silver.groupBy("event_date", "room_id", "event_type").agg(
    F.count("*").alias("event_count"),
    F.countDistinct("player_id").alias("active_players"),
)
daily.orderBy(
    F.col("event_count").desc(),
    "event_date", "room_id", "event_type",
).show(30, truncate=False)
daily.write.mode("errorifexists").partitionBy("event_date").parquet(args.output)

# Gold의 행동 수 합계가 Silver 행 수와 같은지 확인하고 다르면 중단한다.
source_count = silver.count()
# 예시: total_units = items.agg(F.sum("units").alias("n")).first()["n"] or 0
count_sum = daily.agg(F.sum("event_count").alias("n")).first()["n"] or 0
print("source_count =", source_count, "gold_count_sum =", count_sum)
if source_count != count_sum:
    raise ValueError("aggregation count did not conserve events")
spark.stop()
