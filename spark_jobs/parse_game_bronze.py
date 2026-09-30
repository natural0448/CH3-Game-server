import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입출력 경로를 받고 Spark 세션의 시간대를 UTC로 고정한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")

# Kafka 전달 필드와 메시지 본문의 이벤트 필드를 별도 스키마로 정의한다.
outer = "topic STRING, partition INT, offset BIGINT, key STRING, value STRING"
envelope = T.StructType([
    T.StructField("schema_version", T.IntegerType()),
    T.StructField("event_id", T.StringType()),
    T.StructField("event_type", T.StringType()),
    T.StructField("player_id", T.StringType()),
    T.StructField("room_id", T.StringType()),
    T.StructField("event_time", T.StringType()),
    T.StructField("payload", T.MapType(T.StringType(), T.StringType())),
])

# value를 이벤트로 해석하고 전달 위치와 함께 평평한 표로 펼친다.
raw = spark.read.schema(outer).json(args.input)
parsed = raw.withColumn("event", F.from_json("value", envelope))

flat = parsed.select(
    "topic", "partition", "offset", "value",
    "event.schema_version", "event.event_id", "event.event_type",
    "event.player_id", "event.room_id", "event.event_time", "event.payload",
)

# 결과를 미리 본 뒤 새 Parquet 경로에 저장한다. 기존 경로가 있으면 중단한다.
flat.show(5, truncate=False)
flat.write.mode("errorifexists").parquet(args.output)
spark.read.parquet(args.output).select(
    "event_id", "player_id", "room_id"
).show(5, truncate=False)
spark.stop()