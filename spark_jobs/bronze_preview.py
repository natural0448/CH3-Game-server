import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# 입력 경로를 받고 Spark에서 사용할 Kafka 원본 스키마를 정한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-bronze-preview").getOrCreate()

schema = T.StructType([
    T.StructField("topic", T.StringType()),
    T.StructField("key", T.StringType()),
    T.StructField("value", T.StringType()),
    T.StructField("partition", T.IntegerType()),
    T.StructField("offset", T.LongType()),
])

# 원본 전달 위치를 미리 보고 파티션별 행 수와 offset 범위를 확인한다.
raw = spark.read.schema(schema).json(args.input)

raw.select("topic", "partition", "offset").show(5, truncate=False)
raw.groupBy("partition").agg(
    F.count("*").alias("rows"),
    F.countDistinct("key").alias("distinct_keys"),
    F.min("offset").alias("first_offset"),
    F.max("offset").alias("last_offset"),
).orderBy("partition").show(truncate=False)

# 실제 실행 Master를 확인한 뒤 Spark 세션을 닫는다.
print("master =", spark.sparkContext.master)
spark.stop()
