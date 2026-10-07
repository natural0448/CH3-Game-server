"""Game-session Player to public recipient, with server-only media authentication."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

CREATIVE_PATHS = frozenset({"", "/static/ads/creatives/forest-tools.png", "/static/ads/creatives/camp-tea.png"})


class AdsUnavailable(Exception):
    pass


def request_decision(player, slot_id):
    if slot_id not in ("village-board", "lobby-banner"):
        raise ValueError("invalid_slot")
    if not settings.ADS_MEDIA_KEY:
        raise AdsUnavailable("media_key_missing")
    media_id = settings.ADS_MEDIA_ID
    request = Request(settings.ADS_BASE_URL + "/api/media/decision/", method="POST",
                      data=json.dumps({"media_id": media_id,
                          "subject": {"media_id": media_id, "subject_id": str(player.pk)},
                          "slot_id": slot_id, "context": {}}).encode("utf-8"),
                      headers={"Content-Type": "application/json", "Accept": "application/json",
                               "X-Media-Key": settings.ADS_MEDIA_KEY})
    try:
        with urlopen(request, timeout=3) as response:
            raw = response.read(65537)
        if len(raw) > 65536:
            raise ValueError("oversized_response")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("invalid_response")
        if data.get("empty") is True or data.get("ad", "selected") is None:
            return {"ad": None}
        amount = data.get("bid_amount", data.get("bid_units"))
        path = data.get("creative_path", "")
        if (data.get("slot_id") != slot_id or type(amount) is not int or not 1 <= amount <= 10000
                or not isinstance(path, str) or path not in CREATIVE_PATHS):
            raise ValueError("invalid_selection")
        result = {key: data[key] for key in ("decision_id", "campaign_id", "title", "slot_id", "policy_version")}
        if any(not isinstance(value, str) or not value for value in result.values()):
            raise ValueError("invalid_selection")
        body = data.get("body", "")
        if not isinstance(body, str) or len(body) > 300 or len(result["title"]) > 80:
            raise ValueError("invalid_creative")
        return {**result, "body": body, "creative_path": path, "bid_amount": amount,
                "bid_units": amount, "empty": False}
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as exc:
        raise AdsUnavailable("ads_unavailable") from exc
