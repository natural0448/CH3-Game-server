"""Authenticated game relay and a browser check of the same public advertisement."""
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .ad_gateway import AdsUnavailable, request_ad_event, request_decision
from .models import Player


@login_required
@require_GET
def ad_preview(request):
    return render(request, "game/ad_preview.html")


@require_POST
def ad_decision(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    player = Player.objects.filter(user=request.user).first()
    if player is None:
        return JsonResponse({"error": "player_missing"}, status=404)
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid_json"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "invalid_json"}, status=400)
    slot_id = payload.get("slot_id")
    if slot_id not in ("village-board", "lobby-banner"):
        return JsonResponse({"error": "invalid_slot"}, status=400)
    try:
        return JsonResponse(request_decision(player, slot_id))
    except AdsUnavailable:
        return JsonResponse({"error": "ads_unavailable"}, status=503)


@require_POST
def ad_event(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    player = Player.objects.filter(user=request.user).first()
    if player is None:
        return JsonResponse({"error": "player_missing"}, status=409)
    try:
        body = json.loads(request.body)
        if (not isinstance(body, dict)
                or set(body) != {"decision_id", "event_type"}):
            raise ValueError("invalid_ad_event")
        data = request_ad_event(player, body["decision_id"], body["event_type"])
        response = JsonResponse(data)
        response["Cache-Control"] = "no-store"
        return response
    except (ValueError, UnicodeDecodeError) as error:
        code = str(error)
        allowed = {"decision_snapshot_missing", "decision_not_found_for_subject",
                   "impression_required", "decision_id_required", "event_type_invalid"}
        return JsonResponse({"error": code if code in allowed else "ad_event_rejected"}, status=400)
    except AdsUnavailable:
        return JsonResponse({"error": "ads_unavailable"}, status=503)
