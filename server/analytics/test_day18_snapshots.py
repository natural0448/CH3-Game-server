import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve

from analytics.views import load_snapshot, metrics_snapshot


class Day18SnapshotViewTests(SimpleTestCase):
    def request(self, path, authenticated=True):
        request = RequestFactory().get(path)
        request.user = SimpleNamespace(is_authenticated=authenticated)
        return request

    def test_urls_resolve(self):
        self.assertIs(resolve("/api/analytics/load/").func, load_snapshot)
        self.assertIs(resolve("/api/analytics/metrics/").func, metrics_snapshot)

    def test_missing_snapshots_are_not_reported_as_zero(self):
        with TemporaryDirectory() as directory, override_settings(
            DATA_DIR=Path(directory)
        ):
            load = json.loads(
                load_snapshot(self.request("/api/analytics/load/")).content
            )
            metrics = json.loads(
                metrics_snapshot(self.request("/api/analytics/metrics/")).content
            )
        self.assertEqual(load, {"available": False, "load": None})
        self.assertEqual(metrics, {"available": False, "metrics": None})

    def test_load_snapshot_projects_room_totals_without_player_rows(self):
        source = {
            "generated_at": "2026-09-28T06:32:46+00:00",
            "measurement_started_at": "2026-09-28T06:32:16+00:00",
            "profile": {
                "clients": 2,
                "seconds": 30,
                "interval_seconds": 1.0,
                "players_per_room": 20,
                "asgi_processes": 1,
            },
            "connected_success": 2,
            "connected_peak": 2,
            "attempt_count": 60,
            "success_count": 59,
            "error_count": 1,
            "elapsed_seconds": 30.1,
            "success_per_second": 1.96,
            "rtt_sample_count": 59,
            "rtt_mean_ms": 12.5,
            "rtt_p95_ms": 20.0,
            "by_player": [
                {"room_id": "load18-01", "connected": True, "success_count": 30},
                {"room_id": "load18-01", "connected": True, "success_count": 29},
            ],
            "environment": {"private": "not returned"},
        }
        with TemporaryDirectory() as directory, override_settings(
            DATA_DIR=Path(directory)
        ):
            target = Path(directory) / "load" / "run-50.json"
            target.parent.mkdir()
            target.write_text(json.dumps(source), encoding="utf-8")
            with patch("subprocess.run") as run:
                response = json.loads(
                    load_snapshot(self.request("/api/analytics/load/")).content
                )
                run.assert_not_called()
        self.assertTrue(response["available"])
        self.assertNotIn("by_player", response["load"])
        self.assertNotIn("environment", response["load"])
        self.assertEqual(response["load"]["by_room"], [{
            "room_id": "load18-01", "connected": 2, "success_count": 59,
        }])

    def test_metrics_snapshot_reads_published_json_without_running_work(self):
        source = {
            "schema_version": 1,
            "generated_at": "2026-09-28T07:30:00+00:00",
            "window_seconds": 60,
            "confirmed_count": 12,
        }
        with TemporaryDirectory() as directory, override_settings(
            DATA_DIR=Path(directory)
        ):
            target = Path(directory) / "marts" / "game-metrics.json"
            target.parent.mkdir()
            target.write_text(json.dumps(source), encoding="utf-8")
            with patch("subprocess.run") as run:
                response = json.loads(
                    metrics_snapshot(self.request("/api/analytics/metrics/")).content
                )
                run.assert_not_called()
        self.assertEqual(response, {"available": True, "metrics": source})

    def test_login_is_required(self):
        for view, path in (
            (load_snapshot, "/api/analytics/load/"),
            (metrics_snapshot, "/api/analytics/metrics/"),
        ):
            response = view(self.request(path, authenticated=False))
            self.assertEqual(response.status_code, 302)

