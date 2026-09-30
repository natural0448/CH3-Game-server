import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def inspect_file(path):
    """실제 파일 bytes에서 크기, 행 수, 지문을 계산한다."""
    raw = Path(path).read_bytes()
    return {
        "bytes": len(raw),
        "rows": sum(1 for line in raw.splitlines() if line.strip()),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def compare_to_manifest(observed, manifest):
    return {
        key: observed[key] == manifest[key]
        for key in ("bytes", "rows", "sha256")
    }


def make_status(original_path, copied_path, manifest_path):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    original = inspect_file(original_path)
    copied = inspect_file(copied_path)
    original_checks = compare_to_manifest(original, manifest)
    copied_checks = compare_to_manifest(copied, manifest)
    return {
        "schema_version": 1,
        "dataset_id": "village.game-actions",
        "dataset_version": manifest["run_id"],
        "source_topic": manifest["source_topic"],
        "captured_at": manifest["captured_at"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": original["rows"],
        "bytes": original["bytes"],
        "sha256": original["sha256"],
        "verification_scope": "local-and-copied-bytes",
        "original_checks": original_checks,
        "copied_checks": copied_checks,
        "matched": all(original_checks.values()) and all(copied_checks.values()),
    }


def write_status(status, output):
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(target)


def main():
    parser = argparse.ArgumentParser(description="원본·로컬 사본의 마지막 검사 결과 게시")
    parser.add_argument("--original", required=True)
    parser.add_argument("--copied", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="data/marts/lake-status.json")
    args = parser.parse_args()
    status = make_status(args.original, args.copied, args.manifest)
    write_status(status, args.output)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    if not status["matched"]:
        raise SystemExit("selected files do not match the selected manifest")


if __name__ == "__main__":
    main()
