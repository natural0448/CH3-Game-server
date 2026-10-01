import argparse
from pyspark.sql import SparkSession, functions as F

# 입출력 경로를 받고 UTC 세션에서 Silver Parquet을 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)

# 필요한 세 열만 선택해 실행 계획과 행을 확인하고 새 경로에 저장한다.
# errorifexists는 기존 결과 덮어쓰기를 막는다.
selected = df.select("event_date", "room_id", "event_type")
selected.explain("formatted")
selected.show(10, truncate=False)
selected.write.mode("errorifexists").parquet(args.output)
spark.stop()
