import argparse
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent


def resolve_project_path(value):
    """Resolve lesson data paths against the Game-server project root."""
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()

    parts = list(path.parts)
    while parts and parts[0] in (".", ".."):
        parts.pop(0)
    if parts and parts[0].lower() == "data":
        return PROJECT_DIR.joinpath(*parts).resolve()
    return path.resolve()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path", help="측정 결과 JSON 경로(Game-server/data 기준 경로 사용 가능)",
    )
    options = parser.parse_args()
    path = resolve_project_path(options.path)
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        parser.error(f"Result file not found: {path}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        parser.error(f"Result file is not valid UTF-8 JSON: {path}")

    for key in [
        "generated_at", "connected_success", "connected_peak",
        "attempt_count", "success_count", "error_count",
        "elapsed_seconds", "success_per_second",
        "rtt_sample_count", "rtt_mean_ms", "rtt_p95_ms",
    ]:
        print(key, "=", report[key])

    by_room = {}
    for row in report["by_player"]:
        room = row["room_id"]
        item = by_room.setdefault(room, {"players": 0, "success_count": 0})
        item["players"] += int(row["connected"])
        item["success_count"] += row["success_count"]

    print("by_room")
    for room, values in sorted(by_room.items()):
        print(room, values)


if __name__ == "__main__":
    main()
