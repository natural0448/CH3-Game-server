import argparse
import json
from pathlib import Path

# 파일 정리 전후의 화면 집계 JSON을 읽는다.
p = argparse.ArgumentParser()
p.add_argument("--before", required=True)
p.add_argument("--after", required=True)
args = p.parse_args()

old = json.loads(Path(args.before).read_text())
new = json.loads(Path(args.after).read_text())

# 행동 수·행동별·방별 집계를 비교하고 차이가 있으면 계약 발행을 중단한다.
keys = ["event_count", "by_action", "by_room"]
# 예시: matches = {name: before[name] == after[name] for name in fields}
# [문제 2 · 한 줄] keys의 각 지표에 대해 old와 new의 값이 같은지 checks 사전으로 만드는 한 줄을 작성해보세요.
checks = {key: old.get(key) == new.get(key) for key in keys}
print(json.dumps(checks, indent=2))
# [문제 3 · 한 단어] 빈칸을 채워보세요.
if not all(checks.values()):
    raise SystemExit("game metrics changed")

# 검사를 통과하면 새 버전 작성·비교 정책을 기록한다. 이전 데이터는 삭제하지 않는다.
out = Path("data/contracts/compaction-policy.json")
out.write_text(json.dumps({
    "schema_version": 1,
    "strategy": "write-new-version-then-compare",
    "compression": "snappy",
    "target_files_for_small_classroom_data": 2,
    "comparison": checks,
    "previous_data_deleted": False,
}, indent=2), encoding="utf-8")