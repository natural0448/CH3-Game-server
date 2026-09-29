import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# 입력 파일과 실행 ID를 받고 ID에 허용한 문자만 있는지 확인한다.
p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--run-id", required=True)
args = p.parse_args()
if not args.run_id.replace("-", "").isalnum():
    raise ValueError("run-id에 허용한 문자 외 다른 문자열이 존재합니다")

# 원본 bytes를 그대로 새 실행 폴더에 보존한다. 같은 run_id가 있으면 중단한다.
src = Path(args.input)
raw = src.read_bytes()
rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
root = Path("data/lake/bronze/game") / args.run_id
root.mkdir(parents=True, exist_ok=False)
payload = root / "events.ndjson"
payload.write_bytes(raw)

# 파티션별 실제 관찰 offset의 최솟값과 최댓값을 모은다.
ranges = {}
for row in rows:
    part = str(row["partition"])
    value = int(row["offset"])
    current = ranges.setdefault(part, {"min": value, "max": value})
    current["min"] = min(current["min"], value)
    current["max"] = max(current["max"], value)

# 원본의 행 수·길이·지문·offset 범위를 manifest에 함께 저장한다.
manifest = {
    "schema_version": 1, "run_id": args.run_id,
    "source_topic": "game.actions.v1",
    "source_file_name": Path(args.input).name,
    "rows": len(rows), "bytes": len(raw),
    "sha256": hashlib.sha256(raw).hexdigest(),
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "offset_ranges": ranges,
    "data_file": "events.ndjson",
}
(root / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(manifest, ensure_ascii=False, indent=2))
