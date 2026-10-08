# 서버 라우팅 문서

이 색인은 현재 문서화된 서버·Spark 개발 파일과 1:1 짝 문서를 연결한다. 아직 문서화하지 않은 기존 파일을 현재 구조처럼 설명하지 않는다.

## 현재 진행 기준 · 2026-10-08

[현재 진행과 호출 경계](day24-progress.md)를 먼저 읽는다. 22일차 이미지 광고 연결과 23일차 광고 사건 중계는 기존 구현이며, 24일차는 **1교시 공개 Player snapshot 내보내기까지 구현**했다. 공식 1교시 검사는 **12개 통과·0개 실패**다. 실제 입력은 기존 루트 `data/exports/player-cdc.ndjson`에 있고 `server/data`는 없다. 광고의 2교시는 문제틀 작성 중으로 완료되지 않았고 3~8교시는 미적용이다.

상대 출력은 실행 폴더 기준이므로 Game-server 루트에서 `python server/manage.py export_player_snapshot --output data/exports/player-cdc.ndjson`을 사용한다. 광고 작업 폴더의 입력은 `../Game-server/data/exports/player-cdc.ndjson`이다. 파일은 이미 존재하며 초기 검토의 실패 기록과 현재 통과 결과를 구별한다. [이번 문서 정합화 기록](../handoffs/2026-10-08-game-routing-progress-sync.md)과 [기존 경로 정정 기록](../handoffs/2026-10-08-day24-data-path-correction.md)에 근거를 남겼다.

[20일차 8교시 수정·검증](../handoffs/2026-10-01-day20-through-period08.md)은 Bronze→품질→Silver→Gold→화면 요약·계약과 Windows 실행 순서를 기록한다.

2026-09-28 현재 구현 정본의 기존 참조 경로는 `../handoffs/2026-09-28-day18-canonical.md`다. 서버·분석 파이프라인·측정 도구의 기준 상태와 검증 결과를 기록한 문서로 안내되어 있었으나 현재 대상 파일은 없다.

[17일차 Delta 고유 사실 파이프라인 기획](day17-delta-plan.md)은 현재 구현된 Kafka→Delta→집계→분석 API 흐름과 운영 자원 배치를 설명한다.

19일차 7교시까지 반영·검증의 기존 참조 경로는 `../handoffs/2026-09-30-day19-through-period07.md`다. 로컬 Bronze 사본 검사와 기존 Spark Worker 두 대의 미리보기 실행 결과·명령을 기록한 문서로 안내되어 있었으나 현재 대상 파일은 없다.

## Spark 집계

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `spark_jobs/game_batch.py` | `files/spark_jobs/game_batch.py.md` | raw JSONL 또는 Delta 고유 사실을 행동·방별로 일괄 집계해 요약 게시 |
| `spark_jobs/game_actions_delta.py` | `files/spark_jobs/game_actions_delta.py.md` | Kafka 행동 사실을 `event_id` 기준으로 Delta에 고유 저장하고 진행 상태를 기록 |
| `spark_jobs/game_windows.py` | `files/spark_jobs/game_windows.py.md` | 서버 event_time 기준 10초 tumbling·20초 sliding 집계, kind별 Parquet·checkpoint·progress 기록 |
| `spark_jobs/summarize_ingest.py` | `files/spark_jobs/summarize_ingest.py.md` | 수집된 Parquet의 레코드·고유 사건 집계와 선택 UUID 증거 생성 |
| `spark_jobs/summarize_windows.py` | `files/spark_jobs/summarize_windows.py.md` | 확정 시간 창 Parquet에서 종류별 최근 행을 읽어 windows.json 게시 |
| `spark_jobs/bronze_preview.py` | `files/spark_jobs/bronze_preview.py.md` | 기존 Spark 클러스터에서 Bronze 5행과 partition별 행·고유 key·offset 범위 확인 |

## Django 관리 명령

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `server/game/management/commands/export_player_snapshot.py` | `files/server/game/management/commands/export_player_snapshot.py.md` | Player 공개 다섯 필드와 수집 메타데이터를 NDJSON으로 내보내기. 저장소 루트에서 실행해 기존 data/exports 사용 |
| `server/analytics/management/commands/run_game_windows.py` | `files/server/analytics/management/commands/run_game_windows.py.md` | 기존 Spark 클러스터에 시간 창 작업을 제출하는 Django 명령 |
| `server/analytics/management/commands/run_game_delta.py` | `files/server/analytics/management/commands/run_game_delta.py.md` | 기존 Spark 클러스터에 Delta 고유 사실 스트림을 제출하는 Django 명령 |
| `server/analytics/management/commands/summarize_windows.py` | `files/server/analytics/management/commands/summarize_windows.py.md` | 최근 확정 시간 창을 게시하는 Spark 작업 제출 명령 |
| `server/analytics/management/commands/summarize_game.py` | `files/server/analytics/management/commands/summarize_game.py.md` | raw 또는 Delta 행동 집계를 기존 Spark 클러스터에 제출 |
| `server/analytics/management/commands/summarize_ingest.py` | `files/server/analytics/management/commands/summarize_ingest.py.md` | Spark 집계 제출 인자 조립과 프로세스 실행 |
| `server/analytics/management/commands/collect_game_metrics.py` | `files/server/analytics/management/commands/collect_game_metrics.py.md` | DB·publisher·Python 변환기 Kafka 위치·Spark progress를 읽어 운영 snapshot 게시 |
| `server/game/management/commands/run_game_ingest.py` | `files/server/game/management/commands/run_game_ingest.py.md` | Kafka 원천 수집을 driver·executor 1GB 상한으로 제출 |
| `server/game/management/commands/publish_window_demo.py` | `files/server/game/management/commands/publish_window_demo.py.md` | 운영 게임 토픽과 분리된 시간 창 실습용 합성 사건을 단계별 발행 |
| `server/game/management/commands/inspect_game_facts.py` | `files/server/game/management/commands/inspect_game_facts.py.md` | 최근 확정 사실의 세 식별자를 제한된 공개 필드로 읽는 점검 명령 |
| `server/game/management/commands/prepare_load_players.py` | `files/server/game/management/commands/prepare_load_players.py.md` | 수업용 측정 계정과 방별 Player를 만들고 비밀번호 없는 계정 목록을 저장 |
| `server/game/management/commands/export_game_handoff.py` | `files/server/game/management/commands/export_game_handoff.py.md` | 선택한 DB 확정 사실 범위를 UTF-8 JSONL Lake 인계 원본으로 내보내기 |

## 24일차 공개 snapshot 파일

| 현재 데이터 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `data/exports/player-cdc.ndjson` | `files/data/exports/player-cdc.ndjson.md` | 사용자가 생성한 Player 공개 snapshot 원본. 기존 루트 data 폴더에 보관하며 광고의 2교시 입력으로 사용 |
| `.gitignore` | `files/.gitignore.md` | 실제 data 산출물은 제외하고 지정한 snapshot 라우팅 문서만 추적 가능하게 허용 |

## Django 설정

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `config/settings.py` | `files/config/settings.py.md` | Django·MySQL·Channels·Kafka·Spark 및 Delta 패키지 설정의 값 출처 |

## Django 분석 API

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `server/analytics/views.py` | `files/server/analytics/views.py.md` | 게시된 일반·행동·시간 창·운영 지표·부하 측정 JSON의 인증된 읽기 전용 응답 |
| `server/analytics/urls.py` | `files/server/analytics/urls.py.md` | `/api/analytics/` 아래 요약·수집·시간 창·운영·부하·원본 보존 경로 연결 |
| `server/analytics/lake_views.py` | `files/server/analytics/lake_views.py.md` | 인증된 GET으로 게시 Lake 보존 검사 상태만 반환 |
| `server/analytics/test_windows_view.py` | `files/server/analytics/test_windows_view.py.md` | 시간 창 API의 인증·미생성·게시 파일·URL 회귀 검사 |
| `server/analytics/test_day18_snapshots.py` | `files/server/analytics/test_day18_snapshots.py.md` | 운영 지표·부하 snapshot API의 인증·미생성·허용 응답 회귀 검사 |

## Django 게임 HTTP

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `server/game/urls.py` | `files/server/game/urls.py.md` | 관리 화면·게임 화면·인증·Player·전달·이력·광고 미리보기/선택/사건 HTTP 경로 연결 |
| `server/game/views.py` | `files/server/game/views.py.md` | 로컬 전달 현황과 인증된 Player·이력·전달 JSON 응답 |
| `server/game/test_handoff_export.py` | `files/server/game/test_handoff_export.py.md` | Lake 인계 JSONL의 정렬·필드·반개구간·timezone 계약 검사 |

## 로컬 인프라 실행기

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `tools/check_day24_logic.py` | `files/tools/check_day24_logic.py.md` | 24일차 학생 함수를 SQLite 메모리 DB와 임시 파일로 검사하는 교안 원본 도구. 현재 구조에서 1교시는 `--project server` |
| `tools/start-dev.ps1` | `files/tools/start-dev.ps1.md` | Kafka 3노드, 프로필별 Spark Worker 수와 선택적 Docker Compose NiFi의 사전 검사·별도 터미널 실행 |
| `tools/kafka.ps1` | `files/tools/kafka.ps1.md` | Kafka 3노드 초기화·실행·상태·토픽·consumer group 도구 호출 |
| `tools/find_nifi_event.py` | `files/tools/find_nifi_event.py.md` | NiFi JSON 출력 폴더에서 지정한 사건 UUID를 제한 범위로 검색 |
| `tools/ws_load.py` | `files/tools/ws_load.py.md` | 수업 계정별 로그인·WebSocket 이동 요청과 RTT·연결 결과 측정 |
| `tools/read_load_result.py` | `files/tools/read_load_result.py.md` | 저장된 동시 접속 측정 JSON의 대표 지표 출력 |
| `tools/compare_load.py` | `files/tools/compare_load.py.md` | 저장된 두 동시 접속 측정 결과의 입력 조건과 대표 지표 비교 |
| `tools/basics/day19_period03.py` | `files/tools/basics/day19_period03.py.md` | 3교시 bytes 길이·SHA-256 일치 연습 |
| `tools/store_bronze.py` | `files/tools/store_bronze.py.md` | 수집 NDJSON 원본 bytes와 manifest를 새 Bronze 실행 폴더에 저장 |
| `tools/basics/day19_period07.py` | `files/tools/basics/day19_period07.py.md` | 행 수와 서로 다른 key 수 비교 연습 |
| `tools/basics/day19_period01.py` | `files/tools/basics/day19_period01.py.md` | 실제 summary 방 수 계산과 연습 현황 출력 |
| `tools/lake_inventory.py` | `files/tools/lake_inventory.py.md` | 게시 summary와 방 수에서 Lake 저장 현황 JSON 생성 |
| `tools/check_bronze.py` | `files/tools/check_bronze.py.md` | 원본 manifest와 사본의 bytes·rows·SHA-256 비교 및 run_id 출력 |
| `tools/publish_lake_status.py` | `files/tools/publish_lake_status.py.md` | 선택한 원본·로컬 사본을 원본 manifest와 검사해 마지막 원본 보존 상태 게시 |

## Kafka 노드 설정

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `infra/kafka/node1.properties` | `files/infra/kafka/node1.properties.md` | Kafka 1번 노드의 호스트·Docker client listener와 controller 설정 |
| `infra/kafka/node2.properties` | `files/infra/kafka/node2.properties.md` | Kafka 2번 노드의 호스트·Docker client listener와 controller 설정 |
| `infra/kafka/node3.properties` | `files/infra/kafka/node3.properties.md` | Kafka 3번 노드의 호스트·Docker client listener와 controller 설정 |

## 외부 Docker NiFi 구성

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `C:/MLO01-01/nifi-cluster/nifi-compose/compose_cluster.yaml` | `files/external/nifi-compose/compose_cluster.yaml.md` | 교안 기준 PKI 초기화·managed-authorizer·3노드 NiFi/ZooKeeper Compose 구성 |
| `C:/Users/이해나/.wslconfig` | `files/external/wsl/.wslconfig.md` | Docker Desktop WSL VM의 3500MB 메모리·1GB swap 상한과 자동 메모리 회수 설정 |

## 외부 Spark 구성

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `C:/MLO01-01/Chapter3/Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1/conf/spark-env.cmd` | `files/external/spark/conf/spark-env.cmd.md` | Spark Worker 4코어·768MB와 daemon 192MB 환경 설정 |
| `C:/MLO01-01/Chapter3/Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1/conf/spark-defaults.conf` | `files/external/spark/conf/spark-defaults.conf.md` | Spark 기본 driver·executor 768MB와 4 core·4 partition 상한 |

## NiFi 수집 계약

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `data/contracts/nifi-ingestion-plan.json` | `files/data/contracts/nifi-ingestion-plan.json.md` | 확정 행동 토픽을 독립 소비해 JSON 파일로 보존하는 NiFi Flow 계약 |

## 20일차 계층 파이프라인

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `spark_jobs/parse_game_bronze.py` | `files/spark_jobs/parse_game_bronze.py.md` | Bronze JSON 해석 |
| `spark_jobs/check_game_quality.py` | `files/spark_jobs/check_game_quality.py.md` | 품질 검사 |
| `spark_jobs/dedup_game_actions.py` | `files/spark_jobs/dedup_game_actions.py.md` | 행동 중복 제거 |
| `spark_jobs/add_game_date.py` | `files/spark_jobs/add_game_date.py.md` | 한국 날짜 추가 |
| `spark_jobs/build_game_daily.py` | `files/spark_jobs/build_game_daily.py.md` | 일별 Gold |
| `spark_jobs/publish_game_summary.py` | `files/spark_jobs/publish_game_summary.py.md` | 작은 집계 JSON 게시 |
| `tools/write_layer_contract.py` | `files/tools/write_layer_contract.py.md` | 계층 계약 작성 |
| `infra/run-game-layers.sh` | `files/infra/run-game-layers.sh.md` | 실제 Windows 경로의 단계별 PowerShell 명령 보관 |
| `tools/basics/day20_period01.py` | `files/tools/basics/day20_period01.py.md` | 20일차 1교시 연습 |
| `tools/basics/day20_period02.py` | `files/tools/basics/day20_period02.py.md` | 20일차 2교시 연습 |
| `tools/basics/day20_period03.py` | `files/tools/basics/day20_period03.py.md` | 20일차 3교시 연습 |
| `tools/basics/day20_period04.py` | `files/tools/basics/day20_period04.py.md` | 20일차 4교시 연습 |
| `tools/basics/day20_period05.py` | `files/tools/basics/day20_period05.py.md` | 20일차 5교시 연습 |
| `tools/basics/day20_period06.py` | `files/tools/basics/day20_period06.py.md` | 20일차 6교시 연습 |
| `tools/basics/day20_period07.py` | `files/tools/basics/day20_period07.py.md` | 20일차 7교시 연습 |
| `tools/basics/day20_period08.py` | `files/tools/basics/day20_period08.py.md` | 20일차 8교시 연습 |
| `infra/layer-profile.ps1` | `files/infra/layer-profile.ps1.md` | Windows에서 capture-002 입력·출력 URI 설정 |


## 22일차 추가 파일

| 개발 파일 | 짝 문서 |
|---|---|
| server/game/ad_gateway.py | [문서](files/server/game/ad_gateway.py.md) |
| server/game/ad_views.py | [문서](files/server/game/ad_views.py.md) |
| server/game/static/game/ad_preview.js | [문서](files/server/game/static/game/ad_preview.js.md) |
| server/game/templates/game/ad_preview.html | [문서](files/server/game/templates/game/ad_preview.html.md) |
| server/game/static/ads/creatives/forest-tools.png | [문서](files/server/game/static/ads/creatives/forest-tools.png.md) |
| server/game/static/ads/creatives/camp-tea.png | [문서](files/server/game/static/ads/creatives/camp-tea.png.md) |
| server/game/test_ads.py | [문서](files/server/game/test_ads.py.md) |
| data/evidence/asset-sources.md | [문서](files/data/evidence/asset-sources.md.md) |

## 22일차 이미지 광고 흐름

광고주 폼 → campaign creative_path → 선택 당시 creative snapshot → media API → 게임 세션 Player 중계 → 동일 origin PNG bytes → Pygame main thread image decode/draw/flip. 매체 키는 두 서버 설정에만 존재하며 브라우저/접속기에 전달하지 않는다. 실제 학생 창 관찰은 별도 evidence이며 임시 fixture 검증 결과로 대신 기록하지 않는다.

## 로컬 게임 설정

| 개발 파일 | 짝 문서 |
|---|---|
| server/.env | [문서](files/server/.env.md) |


## 기존 Pygame 사건 전송과 수정 교안 범위

기존 구현의 활성 화면 draw/flip receipt → Controller impression → AuthSession/CSRF → 게임 세션 Player → 두 매체 헤더 인증 → 최초 사건 저장 → 공개 receipt 경로를 보존한다. 최신 수정 교안의 3교시 직접 구현은 server/game/ad_gateway.py의 request_ad_event 본문 세 구간이며 Pygame 노출·클릭은 별도 연결 자료다. 수정1교시는 입찰 반환·선택 snapshot,2교시는 사건 API·광고주 선택/실적 목록이다. 일별 보고서·집계·파일 전달은 미적용이다.


## 교안 정본 대응

정본은22일차 수정 교안과 「현재 ad_server에서 노출·클릭과 광고주 보고서 완성하기」 v2.3의1·2교시다. AST/실습/표23개 대조 및 적응 목록은 ad_server/docs/server-routing/verification/lesson-alignment/source-comparison.json, 실행 순서는 ad_server/README.md에 있다. 기존4인수 선택·bid_amount 스키마·이미지·계정·DB·combined view와 계층을 보존했다. 새 광고주 events 목록은 구현했고 일별 reports/집계/파일전달은 미적용이다. 이전 교안의 자동 접속기 코드는 별도 연결 기능으로 보존했다. 최신 3교시 평가와 구별한다.

최신 3교시는 request_ad_event를 교안의 전체 완성 코드와 동일하게 맞추고, 기존 구조에 없던 call_ads를 같은 파일에 보충했다. 선택 함수·combined view·URL은 보존했다. [함수 문서](files/server/game/ad_gateway.py.md), [진행 안내](../../README.md#23일차-수정-교안--3교시-광고-사건-전달), 검증 증거 verification/day23-request-ad-event/를 따른다. 공식 검증 파일 config/check_day23_period3.py는 로그인 다운로드 제한으로 미저장·미실행이며 임의 검증 파일로 대체하지 않았다.

## 2026-10-07 문서 등록과 교안 차이 검토

[오늘 문서 전체 등록 목록](../../../ad_server/docs/server-routing/reviews/2026-10-07-document-registry.md)에 이 프로젝트 19개를 포함한 전체 106개 문서와 검증 근거를 등록했다. [교안 차이 검토](../../../ad_server/docs/server-routing/reviews/2026-10-07-lesson-deviations.md)와 [본 작업 인수인계](../../../ad_server/docs/handoffs/2026-10-07-document-registration-and-lesson-review.md)를 함께 읽는다. 이전 인수인계는 작업 시점의 이력이며 최신 구조/교안 준수로 확대 해석하지 않는다.

| 개발 파일 | 짝 문서 |
|---|---|
| README.md | [문서](files/README.md.md) |
