import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입출력 경로를 받고 UTC 세션에서 펼친 Bronze 표를 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
p = spark.read.parquet(args.input)

# 시각을 해석하고 조건을 위에서부터 검사해 처음 맞는 사유를 기록한다.
checked = p.withColumn("parsed_time", F.try_to_timestamp("event_time"))
checked = checked.withColumn("reason",
    F.when(F.col("schema_version") != 1, "unsupported_schema")
     .when(F.col("schema_version").isNull(), "missing_schema")
     .when(F.col("event_id").isNull(), "missing_event_id")
     .when(F.col("room_id").isNull(), "missing_room")
     .when(F.col("parsed_time").isNull(), "invalid_time")
     .when(~F.col("event_type").isin(
         "player.moved", "player.gathered", "player.trained"
     ), "unknown_action")
     .when(F.col("event_type").isNull(), "missing_action")
     .otherwise("accepted")
)

# 사유별 건수를 확인하고 정상·격리 결과를 각각 새 경로에 저장한다.

checked.groupBy("reason").count().orderBy("reason").show()
# 예시: clean.filter(F.col("status") == "ready").write.mode("errorifexists").parquet(
#           args.output + "/ready"
#       )
# [문제 5 · 여러 줄] reason이 accepted인 행만 골라 새 accepted 하위 Parquet 경로에 저장하는 코드를 작성해보세요. (3줄)
# 정상 행을 선택한다. reason을 포함한 기존 열은 모두 유지한다.
accepted = checked.filter(F.col("reason") == "accepted")

# 정상 행을 방별로 세어 출력한다.
accepted.groupBy("room_id").count().orderBy("room_id").show()

# 정상 행을 저장한다.
accepted.write.mode("errorifexists").parquet(
    args.output + "/accepted"
)

checked.filter(F.col("reason") != "accepted").write.mode("errorifexists").parquet(
    args.output + "/quarantine"
)



spark.stop()

