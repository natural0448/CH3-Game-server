"""Game account, CSRF and public image relay contracts without a live advertiser."""
import io
import json
from types import SimpleNamespace
from urllib.error import HTTPError
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import resolve

from game.ad_gateway import AdsUnavailable, request_ad_event, request_context, request_decision
from game.views import ad_context
from game.models import Player


def selection():
    return {"decision_id": "decision-test", "campaign_id": "forest-tools", "title": "숲 도구점",
            "body": "도구", "slot_id": "village-board", "policy_version": "highest-bid/v1",
            "bid_units": 30, "creative_path": "/static/ads/creatives/forest-tools.png"}


@override_settings(ADS_BASE_URL="http://127.0.0.1:8001", ADS_MEDIA_ID="village-game", ADS_MEDIA_KEY="test-only-key")
class GatewayTests(SimpleTestCase):
    def test_event_error_codes_are_preserved_without_private_details(self):
        for code in ("decision_snapshot_missing", "decision_not_found_for_subject", "impression_required"):
            error = HTTPError("http://fixture/events", 400, "fixture", {},
                              io.BytesIO(json.dumps({"error": code + ": private detail"}).encode()))
            with self.subTest(code=code), patch("game.ad_gateway.urlopen", side_effect=error):
                with self.assertRaisesRegex(ValueError, "^" + code + "$"):
                    request_ad_event(SimpleNamespace(pk=12), "d1", "impression")
        for status, expected in ((401, ValueError), (503, AdsUnavailable)):
            error = HTTPError("http://fixture/events", status, "fixture", {}, io.BytesIO(b'{}'))
            with patch("game.ad_gateway.urlopen", side_effect=error), self.assertRaises(expected):
                request_ad_event(SimpleNamespace(pk=12), "d1", "impression")

    def test_event_public_receipt_duplicate_and_recipient(self):
        receipt = {"event_id": "d1:impression", "event_type": "impression", "created": False, "secret": "excluded"}
        response = io.BytesIO(json.dumps(receipt).encode())
        response.status = 200
        with patch("game.ad_gateway.urlopen", return_value=response) as opened:
            result = request_ad_event(SimpleNamespace(pk=12), "d1", "impression")
        self.assertEqual(result, {key: receipt[key] for key in ("event_id", "event_type", "created")})
        sent = json.loads(opened.call_args.args[0].data)
        self.assertEqual(opened.call_args.args[0].get_header("X-media-id"), "village-game")
        self.assertEqual(sent["subject"], {"media_id": "village-game", "subject_id": "12"})
        for changes in [{"created": "False"}, {"event_id": "other:impression"}, {"event_type": "click"}]:
            response = io.BytesIO(json.dumps({**receipt, **changes}).encode())
            response.status = 200
            with self.subTest(changes=changes), patch("game.ad_gateway.urlopen", return_value=response), self.assertRaises(AdsUnavailable):
                request_ad_event(SimpleNamespace(pk=12), "d1", "impression")

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
    def test_event_session_csrf_and_spoofed_recipient(self):
        payload = {"decision_id": "d1", "event_type": "impression", "player_id": 999, "subject": {"subject_id": "999"}}
        self.assertEqual(self.client.post("/api/ads/events/", data=json.dumps(payload), content_type="application/json").status_code, 401)
        client = Client(enforce_csrf_checks=True);client.force_login(self.user)
        self.assertEqual(client.post("/api/ads/events/", data=json.dumps(payload), content_type="application/json").status_code, 403)
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        receipt = {"event_id": "d1:impression", "event_type": "impression", "created": False}
        with patch("game.ad_views.request_ad_event", return_value=receipt) as event:
            response = client.post("/api/ads/events/", data=json.dumps(payload), content_type="application/json", HTTP_X_CSRFTOKEN=token)
            self.assertEqual(response.status_code, 400)
            event.assert_not_called()
            response = client.post("/api/ads/events/", data=json.dumps({"decision_id": "d1", "event_type": "impression"}), content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.json(), receipt)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(event.call_args.args[0].pk, self.player.pk)

    def test_event_bad_input_and_outage(self):
        self.client.force_login(self.user)
        for body in ['{', '[]', '{"decision_id":"d1","event_type":[]}', '{"event_type":"click"}']:
            self.assertEqual(self.client.post("/api/ads/events/", data=body, content_type="application/json").status_code, 400)
        with patch("game.ad_views.request_ad_event", side_effect=AdsUnavailable("test")):
            response = self.client.post("/api/ads/events/", data='{"decision_id":"d1","event_type":"impression"}', content_type="application/json")
        self.assertEqual(response.status_code, 503)

    def test_event_snapshot_error_and_missing_player_status(self):
        self.client.force_login(self.user)
        with patch("game.ad_views.request_ad_event", side_effect=ValueError("impression_required")):
            response = self.client.post("/api/ads/events/", data='{"decision_id":"d1","event_type":"click"}', content_type="application/json")
        self.assertEqual(response.json(), {"error": "impression_required"})
        self.assertEqual(response.status_code, 400)
        self.player.delete()
        response = self.client.post("/api/ads/events/", data='{}', content_type="application/json")
        self.assertEqual(response.status_code, 409)

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


@override_settings(ADS_BASE_URL="http://127.0.0.1:8001", ADS_MEDIA_ID="village-game",
                   ADS_MEDIA_KEY="test-only-key")
class PlayerContextTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.player = SimpleNamespace(pk=12)
        self.context = {"player_id": "12", "room_id": "room-01", "coins": 26,
                        "version": 461, "updated_at": "2026-10-13T06:36:55+00:00"}

    def test_logged_in_player_ignores_query_recipient_and_does_not_cache(self):
        self.assertIs(resolve("/api/ads/context/").func, ad_context)
        request = self.factory.get("/api/ads/context/?subject_id=9999")
        request.user = SimpleNamespace(is_authenticated=True, pk=99)
        with patch("game.views.Player.objects.filter") as players, \
                patch("game.views.request_context", return_value=self.context) as lookup:
            players.return_value.first.return_value = self.player
            response = ad_context(request)
        players.assert_called_once_with(user=request.user)
        lookup.assert_called_once_with(self.player)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["subject"]["subject_id"], "12")
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_login_missing_player_and_outage_have_separate_statuses(self):
        request = self.factory.get("/api/ads/context/")
        request.user = SimpleNamespace(is_authenticated=False)
        with patch("game.views.Player.objects.filter") as players:
            self.assertEqual(ad_context(request).status_code, 401)
            players.assert_not_called()
        request.user = SimpleNamespace(is_authenticated=True)
        with patch("game.views.Player.objects.filter") as players:
            players.return_value.first.return_value = None
            self.assertEqual(ad_context(request).status_code, 404)
        with patch("game.views.Player.objects.filter") as players, \
                patch("game.views.request_context", side_effect=AdsUnavailable("fixture")):
            players.return_value.first.return_value = self.player
            response = ad_context(request)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(json.loads(response.content), {"error": "ads_unavailable"})
        self.assertEqual(ad_context(self.factory.post("/api/ads/context/")).status_code, 405)

    def test_context_is_fetched_before_selection_and_passed_as_snapshot(self):
        selection = {"decision_id": "fixture-decision", "slot_id": "village-board",
                     "title": "숲 도구점", "body": "도구", "bid_units": 30,
                     "creative_path": "/static/ads/creatives/forest-tools.png"}
        first = io.BytesIO(json.dumps({"subject": {"media_id": "village-game", "subject_id": "12"},
                                     "context": self.context}).encode())
        second = io.BytesIO(json.dumps(selection).encode())
        with patch("game.ad_gateway.urlopen", side_effect=[first, second]) as opened:
            result = request_decision(self.player, "village-board")
        lookup, choice = [call.args[0] for call in opened.call_args_list]
        self.assertTrue(lookup.full_url.endswith("/api/media/context/"))
        self.assertTrue(choice.full_url.endswith("/api/media/decision/"))
        self.assertEqual(json.loads(lookup.data), {
            "subject": {"media_id": "village-game", "subject_id": "12"}})
        self.assertEqual(json.loads(choice.data)["context"], self.context)
        self.assertEqual(result["bid_amount"], 30)
        self.assertEqual(result["body"], "도구")
        self.assertEqual(result["creative_path"], selection["creative_path"])
        for call in opened.call_args_list:
            self.assertEqual(call.kwargs["timeout"], 1.5)
            self.assertEqual(call.args[0].get_header("X-media-id"), "village-game")

    def test_response_recipient_types_and_timezone_are_validated(self):
        subject = {"media_id": "village-game", "subject_id": "12"}
        invalid = [({**subject, "subject_id": "9999"}, self.context),
                   (subject, {**self.context, "version": True}),
                   (subject, {**self.context, "updated_at": "2026-10-13T06:36:55"}),
                   (subject, {**self.context, "private": "excluded"})]
        for returned_subject, context in invalid:
            response = io.BytesIO(json.dumps({"subject": returned_subject, "context": context}).encode())
            with self.subTest(context=context), patch("game.ad_gateway.urlopen", return_value=response):
                with self.assertRaises(AdsUnavailable):
                    request_context(self.player)
        response = io.BytesIO(json.dumps({"subject": subject, "context": {}}).encode())
        with patch("game.ad_gateway.urlopen", return_value=response):
            self.assertEqual(request_context(self.player), {})
