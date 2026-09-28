# 서버 라우팅 문서

이 색인은 현재 문서화된 서버·Spark 개발 파일과 1:1 짝 문서를 연결한다. 아직 문서화하지 않은 기존 파일을 현재 구조처럼 설명하지 않는다.

[17일차 Delta 고유 사실 파이프라인 기획](day17-delta-plan.md)은 현재 구현된 Kafka→Delta→집계→분석 API 흐름과 운영 자원 배치를 설명한다.

## Spark 집계

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `spark_jobs/game_batch.py` | `files/spark_jobs/game_batch.py.md` | raw JSONL 또는 Delta 고유 사실을 행동·방별로 일괄 집계해 요약 게시 |
| `spark_jobs/game_actions_delta.py` | `files/spark_jobs/game_actions_delta.py.md` | Kafka 행동 사실을 `event_id` 기준으로 Delta에 고유 저장하고 진행 상태를 기록 |
| `spark_jobs/game_windows.py` | `files/spark_jobs/game_windows.py.md` | 서버 event_time 기준 10초 tumbling·20초 sliding 집계, kind별 Parquet·checkpoint·progress 기록 |
| `spark_jobs/summarize_ingest.py` | `files/spark_jobs/summarize_ingest.py.md` | 수집된 Parquet의 레코드·고유 사건 집계와 선택 UUID 증거 생성 |
| `spark_jobs/summarize_windows.py` | `files/spark_jobs/summarize_windows.py.md` | 확정 시간 창 Parquet에서 종류별 최근 행을 읽어 windows.json 게시 |

## Django 관리 명령

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `server/analytics/management/commands/run_game_windows.py` | `files/server/analytics/management/commands/run_game_windows.py.md` | 기존 Spark 클러스터에 시간 창 작업을 제출하는 Django 명령 |
| `server/analytics/management/commands/run_game_delta.py` | `files/server/analytics/management/commands/run_game_delta.py.md` | 기존 Spark 클러스터에 Delta 고유 사실 스트림을 제출하는 Django 명령 |
| `server/analytics/management/commands/summarize_windows.py` | `files/server/analytics/management/commands/summarize_windows.py.md` | 최근 확정 시간 창을 게시하는 Spark 작업 제출 명령 |
| `server/analytics/management/commands/summarize_game.py` | `files/server/analytics/management/commands/summarize_game.py.md` | raw 또는 Delta 행동 집계를 기존 Spark 클러스터에 제출 |
| `server/analytics/management/commands/summarize_ingest.py` | `files/server/analytics/management/commands/summarize_ingest.py.md` | Spark 집계 제출 인자 조립과 프로세스 실행 |
| `server/game/management/commands/run_game_ingest.py` | `files/server/game/management/commands/run_game_ingest.py.md` | Kafka 원천 수집을 driver·executor 1GB 상한으로 제출 |
| `server/game/management/commands/publish_window_demo.py` | `files/server/game/management/commands/publish_window_demo.py.md` | 운영 게임 토픽과 분리된 시간 창 실습용 합성 사건을 단계별 발행 |
| `server/game/management/commands/inspect_game_facts.py` | `files/server/game/management/commands/inspect_game_facts.py.md` | 최근 확정 사실의 세 식별자를 제한된 공개 필드로 읽는 점검 명령 |

## Django 설정

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `config/settings.py` | `files/config/settings.py.md` | Django·MySQL·Channels·Kafka·Spark 및 Delta 패키지 설정의 값 출처 |

## Django 분석 API

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `server/analytics/views.py` | `files/server/analytics/views.py.md` | 게시된 일반·행동·시간 창 분석 JSON의 인증된 읽기 전용 응답 |
| `server/analytics/urls.py` | `files/server/analytics/urls.py.md` | `/api/analytics/` 아래 요약·수집·시간 창 경로 연결 |
| `server/analytics/test_windows_view.py` | `files/server/analytics/test_windows_view.py.md` | 시간 창 API의 인증·미생성·게시 파일·URL 회귀 검사 |

## 로컬 인프라 실행기

| 개발 파일 | 짝 문서 | 책임 |
| --- | --- | --- |
| `tools/start-dev.ps1` | `files/tools/start-dev.ps1.md` | Kafka 3노드, 프로필별 Spark Worker 수와 선택적 Docker Compose NiFi의 사전 검사·별도 터미널 실행 |
| `tools/kafka.ps1` | `files/tools/kafka.ps1.md` | Kafka 3노드 초기화·실행·상태·토픽·consumer group 도구 호출 |
| `tools/find_nifi_event.py` | `files/tools/find_nifi_event.py.md` | NiFi JSON 출력 폴더에서 지정한 사건 UUID를 제한 범위로 검색 |

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
