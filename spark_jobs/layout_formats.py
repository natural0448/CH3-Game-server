import argparse
from pyspark.sql import SparkSession, functions as F

# 동일한 입력을 읽어 JSON과 Parquet 비교를 준비한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)

# payload를 제외한 같은 열을 무압축 JSON과 Snappy Parquet으로 각각 새로 저장한다.
plain = df.drop("payload")
print("=" * 50)
print("=" * 50)
print("원본 행 수", plain.count(), "원본 열 수", len(plain.columns))
print("=" * 50)
print("=" * 50)
plain.write.mode("errorifexists").option("compression", "none").json(args.output + "/json")
plain.write.mode("errorifexists").option("compression", "snappy").parquet(args.output + "/parquet")


# JSON에는 원래 스키마를 적용해 두 형식의 행 수와 자료형을 비교한다.
j = spark.read.schema(plain.schema).json(args.output + "/json")
q = spark.read.parquet(args.output + "/parquet")
print("=" * 50)
print("=" * 50)
print("input", plain.count(), "json", j.count(), "parquet", q.count())
print("json schema", j.schema.simpleString())
print("parquet schema", q.schema.simpleString())
print("=" * 50)
print("=" * 50)
spark.stop()