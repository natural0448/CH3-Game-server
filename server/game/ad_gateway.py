"""Game-session Player to public recipient, with server-only media authentication."""
from datetime import datetime
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

CREATIVE_PATHS = frozenset({"", "/static/ads/creatives/forest-tools.png", "/static/ads/creatives/camp-tea.png"})


class AdsUnavailable(Exception):
    pass


def call_ads(path, payload):
    request = Request(
        settings.ADS_BASE_URL + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "X-Media-ID": settings.ADS_MEDIA_ID,
                 "X-Media-Key": settings.ADS_MEDIA_KEY},
        method="POST",
    )
    try:
        with urlopen(request, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        try:
            body = json.loads(exc.read(65536))
            error = body.get("error", "") if isinstance(body, dict) else ""
            code = error.split(":", 1)[0] if isinstance(error, str) else ""
            if code in {"decision_snapshot_missing", "decision_not_found_for_subject",
                        "impression_required", "decision_id_required", "event_type_invalid"}:
                return exc.code, {"error": code}
        except (ValueError, UnicodeDecodeError, OSError):
            pass
        return exc.code, {"error": "ad_request_rejected"}
    except (URLError, TimeoutError, ValueError):
        return 503, {"error": "ads_unavailable"}


def request_decision(player, slot_id):
    media_id = settings.ADS_MEDIA_ID
    if not settings.ADS_MEDIA_KEY:
        raise AdsUnavailable("media_key_missing")
    payload = {
        "media_id": media_id,
        "subject": {"media_id": media_id, "subject_id": str(player.pk)},
        "slot_id": slot_id,
        "context": request_context(player),
    }
    request = Request(
        settings.ADS_BASE_URL.rstrip("/") + "/api/media/decision/",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "X-Media-ID": media_id, "X-Media-Key": settings.ADS_MEDIA_KEY},
        method="POST",
    )
    try:
        with urlopen(request, timeout=1.5) as response:
            data = json.load(response)
        if not isinstance(data, dict):
            raise ValueError("invalid_response")
        if data.get("empty") is True or data.get("ad", "selected") is None:
            return {**data, "ad": None}
        if data.get("slot_id") != slot_id:
            raise ValueError("slot_mismatch")
        return {**data, "body": data.get("body", ""),
                "bid_amount": data.get("bid_amount", data.get("bid_units"))}
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as error:
        raise AdsUnavailable("ads_unavailable") from error


def request_ad_event(player, decision_id, event_type):
    """Use the logged-in player's identity; clients supply only the event target."""
    if not settings.ADS_MEDIA_KEY:
        raise AdsUnavailable("media_key_missing")
    if (not isinstance(decision_id, str) or not decision_id
            or len(decision_id) > 128 or event_type not in ("impression", "click")):
        raise ValueError("invalid_ad_event")
    payload = {
        "media_id": settings.ADS_MEDIA_ID,
        "subject": {
            "media_id": settings.ADS_MEDIA_ID,
            "subject_id": str(player.pk),
        },
        "decision_id": decision_id,
        "event_type": event_type,
    }
    status, data = call_ads("/api/media/events/", payload)
    if status == 503:
        raise AdsUnavailable("ads_unavailable")
    if status != 200:
        code = data.get("error") if isinstance(data, dict) else None
        allowed = {"decision_snapshot_missing", "decision_not_found_for_subject",
                   "impression_required", "decision_id_required", "event_type_invalid"}
        raise ValueError(code if code in allowed else "ad_event_rejected")
    if (not isinstance(data, dict)
            or data.get("event_id") != decision_id + ":" + event_type
            or data.get("event_type") != event_type
            or type(data.get("created")) is not bool):
        raise AdsUnavailable("invalid_ad_event_response")
    return {name: data[name] for name in ("event_id", "event_type", "created")}


def request_context(player):
    media_id = settings.ADS_MEDIA_ID
    if not settings.ADS_MEDIA_KEY:
        raise AdsUnavailable("media_key_missing")
    subject = {"media_id": media_id, "subject_id": str(player.pk)}
    payload = {"subject": subject}
    headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Media-ID": media_id, "X-Media-Key": settings.ADS_MEDIA_KEY}
    request = Request(
        settings.ADS_BASE_URL.rstrip("/") + "/api/media/context/",
        data=json.dumps(payload, allow_nan=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=1.5) as response:
            data = json.load(response)
        if (not isinstance(data, dict) or data.get("subject") != subject
                or not isinstance(data.get("context"), dict)):
            raise ValueError("invalid_context_response")
        context = data["context"]
        if context:
            if (set(context) != {"player_id", "room_id", "coins", "version", "updated_at"}
                    or context["player_id"] != subject["subject_id"]
                    or not isinstance(context["room_id"], str)
                    or type(context["coins"]) is not int
                    or type(context["version"]) is not int or context["version"] < 0
                    or not isinstance(context["updated_at"], str)):
                raise ValueError("invalid_public_context")
            instant = datetime.fromisoformat(context["updated_at"])
            if instant.tzinfo is None or instant.utcoffset() is None:
                raise ValueError("context_time_requires_timezone")
        return dict(context)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as error:
        raise AdsUnavailable("ads_unavailable") from error