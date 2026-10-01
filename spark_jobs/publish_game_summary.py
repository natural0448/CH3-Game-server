import argparse
from pyspark.sql import SparkSession, functions as F, types as T

# Silver 입력과 화면용 JSON 출력 경로를 받는다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
spark = SparkSession.builder.appName("village-layers").getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")

import json
from datetime import datetime, timezone
from pathlib import Path

# 행동별·방별 집계를 정렬하고 방 수가 100개를 넘으면 수집을 중단한다.
silver = spark.read.parquet(args.input)
actions = silver.groupBy("event_type").count().orderBy("event_type")
rooms = silver.groupBy("room_id").count().orderBy("room_id")
if rooms.count() > 100:
    raise ValueError("too many rooms")

summary = {
    "schema_version": 1,
    "dataset_version": Path(args.input.rstrip("/")).name,
    "source": "silver",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "event_count": silver.count(),
    "by_action": [r.asDict() for r in actions.collect()],
    "by_room": [r.asDict() for r in rooms.collect()],
}

# 완성한 JSON을 임시 파일에 쓴 뒤 최종 화면 파일로 교체한다.
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
tmp = out.with_suffix(out.suffix + ".tmp")
tmp.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
tmp.replace(out)
print(json.dumps(summary, ensure_ascii=False, indent=2))
spark.stop()
