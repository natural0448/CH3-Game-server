import argparse
from pyspark.sql import SparkSession, functions as F

# 측정할 Parquet 입력과 보고서 출력 경로를 받는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-file-layout").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
df = spark.read.parquet(args.input)
import json
from pathlib import Path
from datetime import datetime, timezone

# Parquet 파일의 경로·길이만 조회해 파일 수와 총 bytes를 집계한다.
meta = spark.read.format("binaryFile").option("recursiveFileLookup", "true").option(
    "pathGlobFilter", "*.parquet"
).load(args.input).select("path", "length")
sizes = meta.agg(F.count("*").alias("files"), F.sum("length").alias("bytes")).first()

# 행 수와 파일 통계를 실제 Master·측정 시각과 함께 보고서에 담는다.
report = {
    "schema_version": 1, "source_uri": args.input,
    "rows": df.count(), "files": sizes["files"], "bytes": sizes["bytes"] or 0,
    "master": spark.sparkContext.master,
    "generated_at": datetime.now(timezone.utc).isoformat(),
}
if report["files"] == 0:
    report["average_bytes"] = 0
else:
    report["average_bytes"] = report["bytes"] / report["files"]

# 측정 보고서를 JSON으로 저장하고 출력한다.
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
spark.stop()