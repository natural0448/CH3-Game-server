import json
import os
from datetime import datetime, timezone
from pathlib import Path
from pyspark.sql import SparkSession

# 선택한 Bronze 설명서와 Spark의 실제 quarantine·Silver 행 수를 읽는다.
dataset_version = Path(os.environ["SILVER_URI"].rstrip("/")).name
bronze = json.loads((Path("data/lake/bronze/game") / dataset_version / "manifest.json").read_text(encoding="utf-8"))

spark = SparkSession.builder.appName("layer-contract").getOrCreate()

try:
    quarantine_rows = spark.read.parquet(
        os.environ["QUALITY_URI"].rstrip("/") + "/quarantine"
    ).count()

    silver_rows = spark.read.parquet(
        os.environ["SILVER_URI"]
    ).count()
finally:
    spark.stop()

# 입력 버전, Silver·Gold 위치, 중복 제거 키와 집계 기준을 한 계약에 기록한다.
contract = {
    "schema_version": 1, "dataset_version": dataset_version,
    "input_sha256": bronze["sha256"],
    "bronze_rows": bronze["rows"],
    "silver_rows": silver_rows,
    "quarantine_rows": quarantine_rows,
    "silver_uri": os.environ["SILVER_URI"],
    "gold_uri": os.environ["GOLD_URI"],
    "rules": {
        "schema_version": 1, "dedup_key": "event_id",
        "calendar_timezone": "Asia/Seoul",
        "gold_grain": ["event_date", "room_id", "event_type"],
    },
    "created_at": datetime.now(timezone.utc).isoformat(),

}

# 다음 교시가 참조할 계층 계약을 저장하고 출력한다.
out = Path("data/contracts/layer-contract.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(contract, ensure_ascii=False, indent=2))
