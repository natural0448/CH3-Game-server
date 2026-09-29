import argparse
import json
from pathlib import Path

# 실행 ID와 허용 파일 이름을 검증한 뒤 사본의 로컬 경로를 반환한다.
def copy_path(run_id, filename):
    if not run_id.replace("-", "").isalnum():
        raise ValueError("invalid run_id")
    if filename not in {"events.ndjson", "manifest.json"}:
        raise ValueError("not supported filename")
 
    return Path("data/copies/bronze/game") / run_id / filename

# 파일을 직접 실행하면 같은 수집본의 두 사본 경로와 배치 버전을 출력한다.
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    args = p.parse_args()

    print(json.dumps({
        "payload_path": copy_path(args.run_id, "events.ndjson").as_posix(),
        "manifest_path": copy_path(args.run_id, "manifest.json").as_posix(),
        "layout_version": "v1",
    }, indent=2))