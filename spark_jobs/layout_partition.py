import argparse
from pyspark.sql import SparkSession, functions as F

# 입출력 경로를 받고 날짜가 포함된 Parquet을 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)

# 최대 열 개의 날짜를 확인하고 비어 있으면 중단한다.
dates = [r["event_date"] for r in df.select("event_date").distinct().orderBy("event_date").limit(10).collect()]
if not dates:
    raise ValueError("input has no dates")

# 날짜별 새 경로에 저장한 뒤 첫 날짜를 골라 읽기 계획과 행 수를 확인한다.
df.write.mode("errorifexists").partitionBy("event_date").parquet(args.output)
partitioned = spark.read.parquet(args.output)
chosen = dates[-1]
one_day = partitioned.filter(F.col("event_date") == F.lit(chosen))
one_day.explain("formatted")
one_day.groupBy("event_date").count().show()
print("selected date =", chosen)
spark.stop()