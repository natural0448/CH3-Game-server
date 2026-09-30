import json
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# 로그인한 사용자에게 완성된 검사 상태 파일을 제공한다.
@login_required
def lake_status(request):
    path = Path(settings.BASE_DIR).parent / "data" / "marts" / "lake-status.json"

    # 아직 파일이 없으면 pending, 읽기나 JSON 해석에 실패하면 503을 돌려준다.
    if not path.exists():
        return JsonResponse({
            "schema_version": 1,
            "status": "pending",
            "message": "아직 원본 보존 검사 결과가 없습니다.",
        })
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return JsonResponse({
            "schema_version": 1,
            "status": "unavailable",
            "message": "보존 검사 결과를 지금 읽을 수 없습니다.",
        }, status=503)
    return JsonResponse({
        "schema_version": data["schema_version"],
        "status": "ready",
        "dataset_id": data["dataset_id"],
        "dataset_version": data["dataset_version"],
        "captured_at": data["captured_at"],
        "generated_at": data["generated_at"],
        "rows": data["rows"],
        "bytes": data["bytes"],
        "matched": data["matched"],
        "verification_scope": data["verification_scope"],
    })