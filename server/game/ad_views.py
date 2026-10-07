"""Authenticated game relay and a browser check of the same public advertisement."""
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .ad_gateway import AdsUnavailable, request_decision
from .models import Player


@login_required
@require_GET
def ad_preview(request):
    return render(request, "game/ad_preview.html")


@require_POST
def ad_decision(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    try:
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid_json"}, status=400)
    if not isinstance(payload, dict) or payload.get("slot_id") not in ("village-board", "lobby-banner"):
        return JsonResponse({"error": "invalid_slot"}, status=400)
    player = Player.objects.filter(user=request.user).first()
    if player is None:
        return JsonResponse({"error": "player_missing"}, status=404)
    try:
        return JsonResponse(request_decision(player, payload["slot_id"]))
    except AdsUnavailable:
        return JsonResponse({"error": "ads_unavailable"}, status=503)
