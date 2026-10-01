import argparse
from pyspark.sql import SparkSession, functions as F

# 동일한 Parquet 입력과 새 출력 경로를 준비한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)
import json
import time

# Snappy와 Zstd로 각각 새 경로에 저장하고 쓰기·재읽기 시간을 잰다.
results = []
for codec in ["zstd", "snappy"]:
    target = args.output + "/" + codec
    started = time.perf_counter()
    df.write.mode("errorifexists").option("compression", codec).parquet(target)
    write_seconds = time.perf_counter() - started
    started = time.perf_counter()
    restored = spark.read.parquet(target)

    count = restored.count()
    read_seconds = time.perf_counter() - started

    # 압축 방식별 행 수와 두 시간을 모아 비교 결과로 출력한다.
    results.append({
        "codec": codec,
        "rows": count,
        "write_seconds": round(write_seconds, 4),
        "read_seconds": round(read_seconds, 4)
    })
print(json.dumps(results, indent=2))
spark.stop()