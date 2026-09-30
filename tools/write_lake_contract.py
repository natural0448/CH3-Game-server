import json
import os
from pathlib import Path

# 선택한 Bronze manifest를 읽어 재처리 계약의 입력을 고정한다.
manifest_path = Path("data/lake/bronze/game/capture-001/manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

# 검증한 공유 입력 URI·보존 기간·식별자·시간대·재생성 대상을 기록한다. 재처리는 분석에만 적용한다.
# 30일 정책을 기록해도 이 코드가 원본을 자동 삭제하지는 않는다.
contract = {
    "schema_version": 1,
    "dataset_id": "village.game-actions",
    "dataset_version": manifest["run_id"],
    "source_topic": "game.actions.v1",
    "source_of_game_state": "MySQL game_player",
    "bronze_manifest": str(manifest_path),
    "bronze_uri": "file:///C:/MLO01-01/Chapter3/Game-server/data/copies/bronze/game/capture-001/events.ndjson",     "event_identity": "event_id",
    "transport_identity": ["topic", "partition", "offset"],
    "clock_storage": "UTC",
    "calendar_timezone": "Asia/Seoul",
    "retention_policy": {"days": 30, "automatic_delete_enabled": False},
    "rebuild_targets": ["silver/game_actions", "gold/game_daily", "game-summary.json"],
    "replay_effect": "analytics-only",
    "input_sha256": manifest["sha256"],
}

# 계약 파일을 저장하고 실제 입력 지문과 실행 버전을 출력한다.
out = Path("reports/summary.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(contract, ensure_ascii=False, indent=2))