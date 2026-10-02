import argparse
from pyspark.sql import SparkSession, functions as F

# 동일한 입력을 읽어 태스크 수에 따른 파일 배치를 비교한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)

import json

# 2개·20개 파티션으로 각각 새 경로에 쓰고 실제 파일 수와 행 수를 확인한다.
result = []
# [문제 1 · 한 단어] 빈칸을 채워보세요.
for partitions in [2, 5, 20]:
    path = args.output + "/tasks-" + str(partitions)
    df.repartition(partitions).write.mode("overwrite").parquet(path)
    restored = spark.read.parquet(path)
    result.append({
        "tasks": partitions,
        "files": len(restored.inputFiles()),
        "records": restored.count()
    })
print(json.dumps(result, indent=2))
spark.stop()