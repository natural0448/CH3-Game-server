import argparse
import hashlib
import json
from pathlib import Path

# 로컬 사본과 같은 수집본의 원본 폴더 manifest 경로를 받는다.
p = argparse.ArgumentParser()
p.add_argument("--data", required=True)
p.add_argument("--manifest", required=True)
args = p.parse_args()

# 실제 bytes에서 길이·지문·빈 줄을 제외한 행 수를 계산한다.
raw = Path(args.data).read_bytes()
manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
observed = {
    "bytes": len(raw), 
    "sha256": hashlib.sha256(raw).hexdigest(),
    "rows": len([line for line in raw.splitlines() if line.strip()])
}

# manifest의 세 기준과 비교하고 하나라도 다르면 실패로 종료한다.
checks = {key: observed[key] == manifest[key] for key in observed}
print(json.dumps({
    "run_id": manifest["run_id"],
    "observed": observed,
    "checks": checks,
}, indent=2))
if not all(checks.values()):
    raise SystemExit("copy does not match manifest")
