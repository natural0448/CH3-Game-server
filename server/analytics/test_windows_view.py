import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve

from analytics.views import windows_view


class WindowsContractTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/api/analytics/windows/")
        self.request.user = SimpleNamespace(is_authenticated=True)

    def test_url_resolves_to_windows_view(self):
        self.assertIs(resolve("/api/analytics/windows/").func, windows_view)

    def test_missing_and_published_snapshot_are_read_only(self):
        published = {
            "generated_at": "2026-09-22T13:00:00+09:00",
            "windows": [{
                "kind": "tumbling",
                "window_start": "2026-09-22T12:59:40+09:00",
                "window_end": "2026-09-22T12:59:50+09:00",
                "event_type": "player.moved",
                "count": 3,
            }],
        }
        with TemporaryDirectory() as directory, override_settings(DATA_DIR=Path(directory)):
            missing = json.loads(windows_view(self.request).content)
            self.assertEqual(missing, {"available": False, "windows": []})

            target = Path(directory) / "marts" / "windows.json"
            target.parent.mkdir()
            target.write_text(json.dumps(published), encoding="utf-8")
            with patch("subprocess.run") as run:
                response = json.loads(windows_view(self.request).content)
                run.assert_not_called()
            self.assertEqual(response, {"available": True, **published})

    def test_login_is_required(self):
        self.request.user = SimpleNamespace(is_authenticated=False)
        response = windows_view(self.request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content), {"error": "login_required"})
