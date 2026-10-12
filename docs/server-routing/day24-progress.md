# 현재 진행과 서버 라우팅 · 2026-10-12

게임은 공개 Player snapshot 생산을 담당하고 광고는 검사·준비·fixture·계약·비교·누락 관찰을 담당한다. 앞선 1~7교시 검사 이력과 후속 8교시 공식 24개 검사·실제 파일/계약 인계를 구별해 기록한다. 게임 원본과 after는 각 56행이며 이번에 재수집하지 않았다. 아래는 현재 구현과 확인한 증거다.

| 범위 | 현재 구현과 검증 상태 | 실제 책임 위치 |
|---|---|---|
| 22일차 이미지 광고 연결 | 공개 광고 선택·미리보기·기존 이미지 연결 구현. 기존 검증 이력 유지 | `server/game/ad_gateway.py`, `server/game/ad_views.py`, preview template/static 파일 |
| 23일차 사건 중계 | `request_ad_event` 및 `call_ads` 구현. 기존 교안 AST/계약·격리 테스트 통과 기록 유지. 공식 3교시 검사기는 미저장·미실행 | `server/game/ad_gateway.py` → 광고 `/api/media/events/`; 게임 `/api/ads/events/`는 `ad_views.ad_event` |
| 24일차 1교시 | 공개 snapshot 관리 명령 구현. 공식 검사 **passed=12 / failed=0**. 실제 원본 56행·13,275 bytes | `server/game/management/commands/export_player_snapshot.py` → `data/exports/player-cdc.ndjson` |
| 24일차 2교시 | **완료 검증**: 공식 22 통과·0 실패, 실제 원본 56행·checksum 일치 | 광고 ads/snapshot_intake.py 및 ads/management/commands/inspect_player_snapshot.py |
| 24일차 3교시 | **앞선 완료 검증**: 공식 8 통과·0 실패 | 광고 readiness·write_cdc_readiness |
| 24일차 4교시 | **앞선 완료 검증**: 공식 17 통과·0 실패 및 화면 검사 | 광고 teaching-fixture 해석·원문/summary 명령 |
| 24일차 5교시 | **구현·저장 검증**: 공식 13/0 및 화면 검사, 원본과 계약 일치 | 광고 build_snapshot_contract·write_snapshot_contract |
| 24일차 6교시 | **구현·저장 검증**: 공식 15/0, 실제 변경 1건·새 ID/누락 각 0건 | 게임 기존 export 명령의 별도 after 출력 → 광고 load_rows/compare |
| 24일차 7교시 | **구현·저장 검증**: 공식 10/0, 누락 0건·삭제 추론 불가 | 광고 missing_summary·read_snapshot_missing |
| 24일차 8교시 | **완료 검증**: 공식 24/0, 실제 56행 원본·계약 인계 | 광고 handoff_snapshot·handoff_player_snapshot → ad_server/data/exports/day24-input |

## 현재 호출 경계

```text
GET /ads/preview/
  -> ad_views.ad_preview -> game/ad_preview.html
POST /api/ads/decision/
  -> ad_views.ad_decision -> 로그인 User의 Player 조회
  -> ad_gateway.request_decision -> 광고 선택 HTTP 요청 -> 공개 선택 응답
POST /api/ads/events/
  -> ad_views.ad_event -> 로그인 User의 Player 조회·정확한 두 입력 키 검사
  -> ad_gateway.request_ad_event -> call_ads('/api/media/events/', payload)
  -> 광고 사건 응답의 공개 세 필드 -> 게임 JSON 응답

export_player_snapshot 관리 명령
  -> Player 공개 다섯 필드 ORM 읽기
  -> schema_version/source_kind/captured_at을 더한 8필드 NDJSON
  -> Game-server/data/exports/player-cdc.ndjson
  -> 광고 입력 검사: 2교시 완료 검증 (관리명령은 원본을 읽고 JSON 출력)
  -> 광고 준비 상태·fixture·계약·비교·누락 관찰: 7교시까지 구현·저장 검증
  -> 8교시 인계 함수·명령: 공식 24/0, 수신 폴더의 원본·계약 실제 검증
```

광고 중계 view는 Player를 읽고 gateway를 호출한다. 광고 선택 snapshot·노출/클릭 receipt 저장은 광고 서버의 책임이다. Player 파일 snapshot 생산은 별도 게임 관리 명령의 책임이며 광고 HTTP URL을 추가하지 않는다. 정확한 시그니처·파라미터·반환값·호출 관계는 [gateway](files/server/game/ad_gateway.py.md), [광고 view](files/server/game/ad_views.py.md), [HTTP 경로](files/server/game/urls.py.md), [snapshot 관리 명령](files/server/game/management/commands/export_player_snapshot.py.md)의 1:1 문서를 따른다.

현재 브라우저 미리보기의 `ad_preview.js`는 `/api/ads/decision/`을 fetch한다. 사건 API는 등록되어 있지만 이 미리보기 JS의 호출 대상에는 `/api/ads/events/`가 없다. 기존 Pygame 사건 연결과 브라우저 미리보기를 같은 전송 흐름으로 기록하지 않는다. 기존 중복 `/api/auth/csrf/`·`/api/auth/login/`은 URL 목록에 그대로 있으며 첫 매칭되는 `auth_views`가 선택된다.

## 현재 파일과 실행 위치

기존 데이터 폴더는 **`C:/MLO01-01/Chapter3/Game-server/data`**다. 설정의 `DATA_DIR = PROJECT_DIR / "data"`와 같은 위치다. `manage.py`가 `server/` 아래에 있다는 이유로 `server/data`를 사용하지 않는다. 마감 시 `server/data/exports`에도 별도 사용자 파일 3개가 존재하는 것을 확인했다. 이번 광고 검증 입력은 바깥 `Game-server/data/exports`이며 안쪽 파일은 옮기거나 덮어쓰지 않았다. `export_player_snapshot --output`의 상대 경로는 실행 위치 기준이므로 두 위치를 혼용하지 않는다.

명령은 `target = Path(options["output"])`이므로 상대 출력 경로는 프로세스 실행 폴더를 기준으로 한다. 설정의 DATA_DIR를 자동으로 붙이지 않는다.

```powershell
Set-Location C:\MLO01-01\Chapter3\Game-server
.\server\.venv\Scripts\python.exe -X utf8 -B tools/check_day24_logic.py --project server --period 1
```

최초 생성의 표준 명령은 `python server/manage.py export_player_snapshot --output data/exports/player-cdc.ndjson`이다. 현재 파일은 이미 있으므로 재생성할 필요가 없다. 다음 수집에는 기존 원본을 보존할 새 출력 파일명을 지정한다. `server/`에서 실행한다면 같은 위치를 가리키는 상대 인수는 `../data/exports/player-cdc.ndjson`이다.

광고 작업 폴더에서의 후속 입력 경로는 **`../Game-server/data/exports/player-cdc.ndjson`**다. 파일의 SHA-256은 `6ea30948a1c6924b186676511207bd2099683ca00cf1b1582cb595e6437375d0`이며 [데이터 파일 문서](files/data/exports/player-cdc.ndjson.md)에 공개 스키마와 생산·소비 경계를 기록했다. 이 파일과 검사기 결과는 일반 snapshot의 증거이며 MySQL binlog CDC를 관찰한 증거로 확대 해석하지 않는다.

6교시의 별도 [after 파일](files/data/exports/player-snapshot-after.ndjson.md)은 같은 루트 data/exports에 있다. 광고 입력은 ../Game-server/data/exports/player-snapshot-after.ndjson이다. 이전 원본을 before로 유지했고 사용자 after·광고 계약·결과 JSON 모두 보존했다. 이번 실제 대조는 게임 행동의 성공 응답 자체를 관찰한 것으로 기록하지 않는다.

## 최신 성공 결과와 과거 기록

2026-10-12 현재 5~7교시 구현과 저장본 검토는 [광고 인수인계](../../../ad_server/docs/handoffs/2026-10-12-day24-through-period07-review.md)를 따른다. 이번에는 게임 소스·원본·after를 바꾸거나 공식 1교시를 재실행하지 않았다. 아래 2026-10-08 자료는 앞선 검증 이력이다.

[최초 1교시 검토](../handoffs/2026-10-08-day24-period01-review.md)의 실패 결과는 사용자 수정 전 관찰이다. 해당 역사기록은 보존했다. 현재 구현의 공식 성공 결과는 `verification/day24-data-path-correction/period01-official-current.json`과 [경로 정정 인수인계](../handoffs/2026-10-08-day24-data-path-correction.md)를 따른다. 이번 문서 작업에서의 재검사 결과는 `verification/day24-routing-sync/agent-period01-current.json`에 기록한다.

공식 1교시 checker는 SQLite 메모리 DB와 임시 파일에서 학생 함수를 실행하며 실제 MySQL·MongoDB에 쓰지 않는다. 검사 논리와 실제 파일의 무결성은 별도 검사다. 이번 작업의 Git 경계·기존 변경·문서 수정·최종 정합화 검증은 [인수인계](../handoffs/2026-10-08-game-routing-progress-sync.md)를 따른다.

## 8교시 실제 인계 완료

광고가 기존 바깥 Game-server/data/exports/player-cdc.ndjson과 5교시 계약을 검증한 뒤 광고 data/exports/day24-input에 인계했다. 56행·checksum·원본 bytes가 유지되고 수신 계약은 source_path만 바뀐다. 게임 원본을 재수집하거나 게임 소스를 수정하지 않았다. [광고 완료 기록과 사용자 명령](../../../ad_server/docs/handoffs/2026-10-12-day24-period08-finish.md)을 따른다. 25일차 소비 입력은 광고 수신 폴더의 player-cdc.ndjson이다.
