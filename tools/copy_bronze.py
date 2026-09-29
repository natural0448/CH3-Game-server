import argparse
import json
from pathlib import Path
from local_paths import copy_path

# 실행 ID를 받고 두 사본 경로를 계산하면서 입력을 먼저 검증한다.
p = argparse.ArgumentParser()
p.add_argument("--run-id", required=True)
args = p.parse_args()
payload_copy = copy_path(args.run_id, "events.ndjson")
manifest_copy = copy_path(args.run_id, "manifest.json")

# 원본 폴더에서 이벤트와 설명서의 바이트를 모두 읽는다.
source = Path("data/lake/bronze/game") / args.run_id
payload_bytes = (source / "events.ndjson").read_bytes()
manifest_bytes = (source / "manifest.json").read_bytes()

payload_copy.parent.mkdir(parents=True, exist_ok=False)

# 이벤트 사본을 먼저 기록하고 같은 수집본의 설명서를 나중에 기록한다.
payload_copy.write_bytes(payload_bytes)
manifest_copy.write_bytes(manifest_bytes)

# 실제 사본 파일의 이름과 바이트 수를 모아 출력한다.
files = [
    {"name": payload_copy.name, "bytes": len(payload_copy.read_bytes())},
    {"name": manifest_copy.name, "bytes": len(manifest_copy.read_bytes())},
]
print(json.dumps({
    "run_id": args.run_id,
    "directory": payload_copy.parent.as_posix(),
    "files": files,
}, indent=2))