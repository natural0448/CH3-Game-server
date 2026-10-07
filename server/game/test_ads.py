"""Game account, CSRF and public image relay contracts without a live advertiser."""
import io
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase, override_settings

from game.ad_gateway import AdsUnavailable, request_decision
from game.models import Player


def selection():
    return {"decision_id": "decision-test", "campaign_id": "forest-tools", "title": "숲 도구점",
            "body": "도구", "slot_id": "village-board", "policy_version": "highest-bid/v1",
            "bid_units": 30, "creative_path": "/static/ads/creatives/forest-tools.png"}


@override_settings(ADS_BASE_URL="http://127.0.0.1:8001", ADS_MEDIA_ID="village-game", ADS_MEDIA_KEY="test-only-key")
class GatewayTests(SimpleTestCase):
    def test_public_player_identity_and_legacy_amount_are_adapted(self):
        payload = {**selection(), "secret": "excluded", "owner_user_id": 99}
        with patch("game.ad_gateway.urlopen", return_value=io.BytesIO(json.dumps(payload).encode())) as opened:
            result = request_decision(SimpleNamespace(pk=12), "village-board")
        sent = json.loads(opened.call_args.args[0].data)
        self.assertEqual(sent["subject"], {"media_id": "village-game", "subject_id": "12"})
        self.assertEqual(result["bid_amount"], 30)
        self.assertNotIn("secret", result)
        self.assertNotIn("owner_user_id", result)

    def test_empty_and_invalid_response_or_missing_key(self):
        with patch("game.ad_gateway.urlopen", return_value=io.BytesIO(b'{"ad": null}')):
            self.assertEqual(request_decision(SimpleNamespace(pk=12), "village-board"), {"ad": None})
        for changes in [{"creative_path": "https://example.com/image.png"}, {"slot_id": "lobby-banner"},
                        {"bid_units": True}]:
            with self.subTest(changes=changes), patch("game.ad_gateway.urlopen",
                    return_value=io.BytesIO(json.dumps({**selection(), **changes}).encode())):
                with self.assertRaises(AdsUnavailable):
                    request_decision(SimpleNamespace(pk=12), "village-board")
        with override_settings(ADS_MEDIA_KEY=""), self.assertRaises(AdsUnavailable):
            request_decision(SimpleNamespace(pk=12), "village-board")


class RelayTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ads-player")
        self.player = Player.objects.create(user=self.user)

    def test_login_post_only_and_current_player_ignore_spoofed_subject(self):
        self.assertEqual(self.client.post("/api/ads/decision/", data='{}', content_type="application/json").status_code, 401)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/api/ads/decision/").status_code, 405)
        with patch("game.ad_views.request_decision", return_value=selection()) as request:
            response = self.client.post("/api/ads/decision/", data=json.dumps({
                "slot_id": "village-board", "player_id": 999, "subject": {"subject_id": "999"},
            }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.call_args.args[0].pk, self.player.pk)

    def test_csrf_is_required_for_game_relay(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        payload = json.dumps({"slot_id": "village-board"})
        self.assertEqual(client.post("/api/ads/decision/", data=payload, content_type="application/json").status_code, 403)
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        with patch("game.ad_views.request_decision", return_value=selection()):
            response = client.post("/api/ads/decision/", data=payload,
                                   content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)

    def test_invalid_input_outage_and_preview(self):
        self.client.force_login(self.user)
        for body in ['{', '[]', '{"slot_id": []}', '{"slot_id": "unknown"}']:
            with self.subTest(body=body):
                self.assertEqual(self.client.post("/api/ads/decision/", data=body, content_type="application/json").status_code, 400)
        with patch("game.ad_views.request_decision", side_effect=AdsUnavailable("test")):
            self.assertEqual(self.client.post("/api/ads/decision/", data='{"slot_id":"village-board"}',
                                             content_type="application/json").status_code, 503)
        self.assertContains(self.client.get("/ads/preview/"), 'id="request-ad"')
