# `server/analytics/urls.py`

## 책임과 경로

`config.urls`의 `/api/analytics/` prefix 아래 분석 조회 뷰를 연결한다.

- `""` → `views.summary_view`, 이름 `summary`.
- `"ingest/"` → `ingest_summary_view`, 이름 `ingest-summary`.
- `"windows/"` → `views.windows_view`, 이름 `windows`.

따라서 시간 창 조회의 외부 경로는 `GET /api/analytics/windows/`이다.

