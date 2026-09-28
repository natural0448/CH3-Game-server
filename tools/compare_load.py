import argparse
import json
from pathlib import Path


def display_number(value, digits=3):
    return "측정값 없음" if value is None else round(value, digits)


def percent_change(before, after):
    if before is None or after is None or before == 0:
        return None
    return (after - before) / before * 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("left")
    parser.add_argument("right")
    options = parser.parse_args()
    paths = [Path(options.left), Path(options.right)]
    reports = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in paths
    ]

    for path, report in zip(paths, reports):
        profile = report["profile"]
        requested = profile["clients"]
        connected = report["connected_success"]
        peak = report["connected_peak"]
        print("file:", path)
        print("clients:", requested)
        print("interval_seconds:", profile["interval_seconds"])
        print("requested_seconds:", profile["seconds"])
        print("observed_seconds:", display_number(report["elapsed_seconds"]))
        print("connected_success:", connected)
        print("connected_peak:", peak)
        print("requested / connected / peak:", requested, "/", connected, "/", peak)
        print("success_count:", report["success_count"])
        print("error_count:", report["error_count"])
        print("success_per_second:", display_number(report["success_per_second"]))
        print("rtt_p95_ms:", display_number(report["rtt_p95_ms"]))

    same_interval = (
        reports[0]["profile"]["interval_seconds"]
        == reports[1]["profile"]["interval_seconds"]
    )
    same_duration = (
        reports[0]["profile"]["seconds"]
        == reports[1]["profile"]["seconds"]
    )
    print("same_interval:", same_interval)
    print("same_requested_duration:", same_duration)
    for key in ("success_per_second", "rtt_p95_ms"):
        change = percent_change(reports[0].get(key), reports[1].get(key))
        print(f"{key}_change_percent:", display_number(change))


if __name__ == "__main__":
    main()
