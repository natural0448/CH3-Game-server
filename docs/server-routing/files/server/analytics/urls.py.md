# `server/analytics/urls.py`

## 책임과 경로

`config.urls`의 `/api/analytics/` prefix 아래 분석 조회 뷰를 연결한다.

- `""` → `views.summary_view`, 이름 `summary`.
- `"ingest/"` → `ingest_summary_view`, 이름 `ingest-summary`.
- `"windows/"` → `views.windows_view`, 이름 `windows`.
- `"metrics/"` → `views.metrics_snapshot`, 이름 `metrics-snapshot`.
- `"load/"` → `views.load_snapshot`, 이름 `load-snapshot`.
- `"lake/"` → `lake_status`, 이름 `lake-storage-status`. 상위 include prefix와 합쳐 외부 경로는 `GET /api/analytics/lake/`다.

따라서 추가 운영 snapshot 외부 경로는 `GET /api/analytics/metrics/`와 `GET /api/analytics/load/`이다.
