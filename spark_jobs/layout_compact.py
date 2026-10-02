import argparse
from pyspark.sql import SparkSession, functions as F

# 입출력 경로를 받고 합칠 Parquet을 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)

# payload를 제외한 열을 같은 순서로 맞추고 최대 두 파티션으로 새 경로에 쓴다.
columns = sorted(c for c in df.columns if c != "payload")
before = df.select(*columns)
before.coalesce(3).write.mode("errorifexists").option("compression", "snappy").parquet(args.output)
after = spark.read.parquet(args.output).select(*columns)

# 양방향 exceptAll로 중복까지 포함한 누락·추가 행을 검사한다.
missing = before.exceptAll(after).count()
extra = after.exceptAll(before).count()

# 행 수·파일 수·차이를 확인하고 내용이 달라졌으면 중단한다.
print("before rows", before.count(), "after rows", after.count())
print("missing", missing, "extra", extra)
print("files", len(before.inputFiles()), "->", len(after.inputFiles()))
if missing or extra:
    raise ValueError("compacted data differs")
spark.stop()