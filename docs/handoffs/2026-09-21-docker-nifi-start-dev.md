# 교안 기준 Docker NiFi 관리자 권한·Kafka 연결 인수인계

## 요청 목적과 완료 결과

변경된 15일차 7교시 교안을 기준으로 기존 `C:/MLO01-01/nifi-cluster/nifi-compose` 폴더 구조를 유지하면서 NiFi 2.12.0 세 노드를 다시 구성했다. `.env`의 로그인 비밀번호를 사용하는 `admin`을 `managed-authorizer`의 초기 관리자로 등록했고, 세 노드 인증서 DN을 초기 사용자와 `Node Identity`에 등록했다.

NiFi는 Docker bridge에서 실행되므로 호스트 Kafka가 별도 listener를 제공하도록 세 broker에 29092·29094·29096 포트를 추가했다. 호스트 Django·publisher·변환기는 기존 9092·9094·9096을 계속 사용한다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `e24b87e 15day - 6교시`
- staged 변경: 없음
- 작업 시작 전에 존재한 수정:
  - `docs/server-routing/README.md`
  - `tools/start-dev.ps1`
  - `한번에_실행.md`
- 작업 시작 전에 존재한 untracked:
  - `docs/handoffs/2026-09-18-nifi-infra-launcher.md`
  - `docs/handoffs/2026-09-21-docker-nifi-start-dev.md`
  - `docs/server-routing/files/tools/`
  - `tools/find_nifi_event.py`

기존 변경은 보존하고 현재 코드와 맞는 라우팅 문서를 먼저 유지한 뒤 이번 설정을 추가했다.

## 이번 작업에서 변경한 파일

### Git 저장소 안

- 수정: `infra/kafka/node1.properties`, `node2.properties`, `node3.properties`
  - 호스트용 `PLAINTEXT` listener를 유지했다.
  - Docker NiFi용 `DOCKER` listener와 advertised 주소를 수정 교안 기준 29092·29094·29096에 추가했다.
- 수정: `tools/start-dev.ps1`
  - 세 Docker listener 포트를 서비스 충돌 검사에 추가했다.
  - Compose 사전 검사에서 교안의 `initialize` 서비스도 확인한다.
- 수정: `한번에_실행.md`
  - admin 권한 구성, NiFi용 Kafka 주소, 검증 명령과 비밀번호 변경 주의를 기록했다.
- 수정: `docs/server-routing/README.md`
  - Kafka 설정 3개와 외부 Compose의 1:1 문서를 색인에 추가했다.
- 추가: `docs/server-routing/files/infra/kafka/node1.properties.md`
- 추가: `docs/server-routing/files/infra/kafka/node2.properties.md`
- 추가: `docs/server-routing/files/infra/kafka/node3.properties.md`
- 추가: `docs/server-routing/files/external/nifi-compose/compose_cluster.yaml.md`
- 추가: `docs/server-routing/files/external/wsl/.wslconfig.md`
- 갱신: `docs/server-routing/files/tools/start-dev.ps1.md`
- 갱신: 이 인수인계 문서

### Git 저장소 밖의 기존 폴더

- 수정: `C:/MLO01-01/nifi-cluster/nifi-compose/compose_cluster.yaml`
  - 교안의 `initialize`, 공통 CA, 노드별 인증서, healthcheck, `verify` 구조를 적용했다.
  - 로그인 아이디는 `admin`, 비밀번호 출처는 기존 `.env`의 `NIFI_PASSWORD`다.
  - `Initial Admin Identity=admin`, 세 `Node Identity`와 `managed-authorizer`를 구성한다.
  - `/work/output`은 기존 `Game-server/data/nifi/game-actions`에 연결한다.
  - NiFi 컨테이너에 `host.docker.internal` 호스트 게이트웨이를 제공한다.
- 기존 `.env` 파일과 폴더 구조는 유지했다. 비밀값은 문서나 출력에 복사하지 않았다.
- 변경 전 Compose 백업: `compose_cluster.yaml.before-auto-managed-authorizer-20260921-111955.bak`
- 추가: `C:/Users/이해나/.wslconfig`
  - WSL VM memory 4GB, swap 1GB, page reporting과 gradual auto reclaim을 설정했다.

## 설계 결정과 책임 경계

- 첫 관리자도 권한이 있어야 UI에서 다른 정책을 편집할 수 있으므로 Compose 초기화가 `admin`을 `Initial Admin Identity`로 한 번 등록한다. 이후 사용자는 NiFi 화면에 admin으로 들어가 사용자와 접근 정책을 관리한다.
- 저장된 `users.xml`, `authorizations.xml`, flow 또는 다른 sensitive key가 있는 미관리 conf는 자동으로 덮어쓰지 않는다.
- 초기화 이후 `.env` 비밀번호가 저장된 값과 다르면 자동 교체하지 않고 중단한다.
- NiFi의 Kafka Controller Service에는 `host.docker.internal:29092,29094,29096`을 사용한다. Processor와 Flow 생성은 Compose나 실행기가 대신하지 않는다.
- `start-dev.ps1`은 설정 존재와 포트만 검사하고 비밀번호·인증서·NiFi Flow를 출력하거나 변경하지 않는다.

## Kafka 메타데이터 복구

Docker listener 검증을 위해 Kafka를 시작할 때 node1·node2 메타데이터 로그 끝에 잘못된 0바이트 레코드가 있어 시작이 중단됐다. `kafka-dump-log.bat`으로 마지막 정상 레코드의 끝 위치를 확인하고 세 노드의 `__cluster_metadata-0` 폴더를 먼저 백업한 뒤 node1·node2의 손상된 꼬리만 제거했다.

- 백업: `data/kafka-metadata-backup-20260921-112808`
- 보존: 모든 토픽 데이터와 node3의 최신 정상 메타데이터
- 복구 후: controller leader 선출, follower lag 0, `game.events.v1` 세 partition의 ISR 3개 확인

## 라우팅 문서 정합화

- Kafka 설정 세 파일은 `docs/server-routing/files/infra/kafka/`의 문서와 1:1로 연결했다.
- 외부 Compose는 `docs/server-routing/files/external/nifi-compose/compose_cluster.yaml.md`와 연결했다.
- 사용자 WSL 설정은 `docs/server-routing/files/external/wsl/.wslconfig.md`와 연결했다.
- 실행기는 `docs/server-routing/files/tools/start-dev.ps1.md`와 대조했다.
- 전체 연결은 `docs/server-routing/README.md` 색인에 반영했다.

## 검사 명령과 결과

```powershell
docker compose config --quiet
docker compose up -d
docker compose ps
docker compose --profile tools run --rm verify
```

## 후속 Docker 볼륨 정리

사용자 승인 후 기존 단일 NiFi 구성과 어떤 컨테이너도 참조하지 않는 볼륨을 삭제했다. 이후 교안의 Compose 선언과 현재 컨테이너 mount를 다시 대조했다.

- 이전 정리에서 삭제: 단일 NiFi 구성의 `day15-nifi_*` 7개와 미참조 익명 볼륨 11개
- 이번 정리에서 삭제: 종료된 `initialize` 컨테이너와 그 전용 익명 볼륨 9개
- 보존: 교안이 선언한 `day15-nifi-zk_*` named volume 31개
- 보존: 실행 중인 공식 이미지가 요구하는 0B 익명 볼륨 9개
  - ZooKeeper `/logs` 3개
  - NiFi `nar_extensions`·`python_extensions` 6개
- `day15-nifi-zk_private`는 현재 컨테이너 미참조로 표시되지만 CA·개인키·관리자 설정을 담은 필수 볼륨이라 보존

공식 이미지의 9개 익명 볼륨은 실행 중 삭제할 수 없고 같은 이미지로 컨테이너를 다시 만들면 자동 생성된다. 교안의 영구 데이터 볼륨을 넘어서는 사용 데이터는 남기지 않았고, `docker volume prune`은 `private`를 지울 수 있어 실행하지 않았다. 정리 후 NiFi 3개와 ZooKeeper 3개는 모두 healthy다.

Compose 재시작으로 `initialize`가 다시 만들어졌다면 NiFi가 healthy가 된 뒤 Compose 폴더에서 `docker compose --env-file .env -f compose_cluster.yaml rm -f -v initialize`를 실행한다. 이 명령은 종료된 초기화 컨테이너와 그 전용 익명 볼륨만 제거한다.

## 후속 WSL 4GiB 메모리 상한 적용

볼륨 개수와 RAM 제한을 구분해 실제 컨테이너 사용량과 디스크 사용량을 확인했다. 볼륨은 RAM을 예약하지 않았으며, 변경 전 실제 지속 실행 메모리는 약 3.5GiB이고 Compose 제한 합계는 7.5GiB였다.

- NiFi: 노드당 `mem_limit=960m`, heap init 256m, heap max 576m
- ZooKeeper: 노드당 `mem_limit=144m`, JVM Xms 64m, Xmx 96m
- 지속 실행 컨테이너 상한 합계: 3312MiB
- WSL: `C:/Users/이해나/.wslconfig`에서 memory 4GB, swap 1GB, page reporting과 gradual auto reclaim 설정
- 변경 전 Docker VM 인식 메모리 7.44GiB, 변경 후 3.82GiB
- 변경 전 VmmemWSL working set 5.46GiB, 변경 직후 3.98GiB
- Compose 백업: `C:/MLO01-01/nifi-cluster/nifi-compose/compose_cluster.yaml.before-wsl-4g-20260921-124124.bak`
- 재생성 후 NiFi 3개·ZooKeeper 3개 모두 healthy
- `verify`: TLS, admin 로그인, CONNECTED 3개, heartbeat 진행 모두 PASS
- 완료된 initialize 컨테이너와 그 전용 익명 볼륨 삭제
- `day15-nifi-zk_private`는 CA·관리자 설정의 필수 볼륨이므로 컨테이너 미참조 상태에서도 보존
- WSL·Docker 재시작 전후의 Django runserver 4개와 publisher 2개 PID가 모두 유지됨

현재 실행 노드가 참조하는 repository·TLS·conf·ZooKeeper 볼륨은 기능 및 재시작 복구에 필요해 삭제하지 않았다.

## 확장 타입 첫 조회 timeout 조정

Processor·Controller Service 생성 화면의 `/nifi-api/flow/processor-types` 요청이 한 번 실패했다. `nifi1` 로그의 직접 원인은 인증서나 권한 문제가 아니라 `java.net.http.HttpTimeoutException`이었다. 기본 `nifi.cluster.node.read.timeout=5 sec`인 상태에서 재시작 후 첫 확장 목록 생성은 5.701초가 걸려 제한을 넘었다.

- 포함 `start-node.py`에 `set_property(name, value)`를 추가했다.
- 세 노드에 `nifi.cluster.node.read.timeout=30 sec`를 재시작마다 적용한다.
- 기존 `nifi.web.request.timeout=60 secs`와 connection timeout 5초는 유지한다.
- 재시작 직후 인증된 `/nifi-api/flow/processor-types` 확인: HTTP 200, processor type 294개
- 변경 후 `verify`: TLS·admin 로그인·CONNECTED 3개·heartbeat 진행 모두 PASS
- 변경 전 백업: `C:/MLO01-01/nifi-cluster/nifi-compose/compose_cluster.yaml.before-cluster-read-timeout-20260921-133819.bak`

## Kafka Controller Service 활성화

NiFi Flow 범위의 `Kafka3ConnectionService`는 설정이 Valid였지만 생성 후 활성화 동작이 실행되지 않아 Disabled로 남아 있었다. 다음 항목을 확인한 뒤 run-status를 Enabled로 변경했다.

- 표시 이름: `Village local Kafka · actions read`
- Bootstrap Servers: `host.docker.internal:29092,29094,29096`
- Security Protocol: `PLAINTEXT`
- NiFi 컨테이너에서 세 broker 포트 모두 TCP 연결 성공
- 세 NiFi 노드에서 모두 상태 `ENABLED`, 검증 상태 `VALID`, validation error 없음

NiFi UI에서 `Apply`는 속성 저장만 수행한다. 새 Controller Service는 목록의 번개 아이콘 또는 오른쪽 메뉴에서 `Enable`을 별도로 실행해야 한다.

- ZooKeeper 3개와 NiFi 3개 모두 healthy.
- 공통 CA와 노드 hostname TLS 검증 통과.
- admin으로 세 NiFi URL 인증 성공.
- Cluster API에서 세 노드 모두 CONNECTED.
- 두 번의 관찰 사이에 heartbeat가 진행됨.

```powershell
.\tools\kafka.ps1 -Action status
.\tools\kafka.ps1 -Action describe-topic
```

- KRaft leader 선출과 follower lag 0 확인.
- `game.events.v1`: partition 3, replication factor 3, 각 ISR 3 확인.
- nifi1 컨테이너에서 `host.docker.internal`의 29092·29094·29096 TCP 연결 성공.

```powershell
.\start-dev.cmd -CheckOnly
```

- PowerShell parser와 `git diff --check` 통과.
- Docker Engine·Compose v2, `.env` 보간, `initialize`·ZooKeeper·NiFi 서비스 사전 검사 통과.
- 라우팅 색인의 이번 개발 파일·짝 문서 6쌍이 모두 존재함을 확인.
- 검사 시 Kafka 포트는 비어 있었고 NiFi 포트는 실행 중이었다. 기존 Spark Master·Worker 포트도 사용 중이었으나 이번 작업에서는 Spark를 시작하거나 종료하지 않았다.

검증을 위해 실행한 Kafka 세 노드는 종료했다. Spark는 시작하지 않았다. 기존 Docker NiFi·ZooKeeper 스택은 새 구성을 적용한 뒤 healthy 상태로 유지했다.

## 남은 위험과 후속 작업

- NiFi Canvas의 Controller Service와 ConsumeKafka·PutFile Flow는 구성되어 실행 중이다. Docker NiFi를 중지한 뒤 다시 시작해도 저장된 flow와 consumer group 진행 위치를 삭제하지 않는다.
- 로컬 CA를 Windows 브라우저가 신뢰하지 않으면 첫 접속에 인증서 안내가 보일 수 있다.
- `data/kafka-metadata-backup-20260921-112808`은 복구 확인용이므로 바로 삭제하지 않는다.

## 다음 시작·확인 순서

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\start-dev.cmd -CheckOnly
.\start-dev.cmd
```

NiFi 접속:

```text
https://localhost:8443/nifi/
아이디: admin
비밀번호: C:\MLO01-01\nifi-cluster\nifi-compose\.env의 NIFI_PASSWORD 값
```

NiFi Kafka Controller Service의 Bootstrap Servers:

```text
host.docker.internal:29092,host.docker.internal:29094,host.docker.internal:29096
```

## 8교시 작성 1~3 완료

교안에 맞춰 NiFi 루트 아래 `Village independent ingest` Process Group을 만들고 독립 수집 Flow를 구성했다.

```text
ConsumeKafka actions
  topic: game.actions.v1
  group: village-nifi-actions-v1
  auto.offset.reset: earliest
  processing strategy: FLOW_FILE
  commit offsets: true
  concurrent tasks: 1

PutFile game actions
  directory: /work/output
  create missing directories: true
  conflict resolution: fail
  concurrent tasks: 1
```

`ConsumeKafka actions`의 success를 `PutFile game actions`로 연결했고 PutFile success는 auto terminate로 설정했다. 교안의 PutFile failure 자기 연결은 무제한 실패 반복 위험 때문에 적용하지 않았다. 대신 failure를 최대 10회, 최대 10분 backoff로 재시도한 뒤 `failed files for manual inspection` Funnel 앞 queue에 보존하도록 구성했다.

PutFile을 먼저 시작하고 ConsumeKafka를 시작했다. 두 Processor는 RUNNING·VALID 상태다. 기존 루트에 남아 있던 잘못된 Windows 출력 경로의 PutFile과 unconnected ConsumeKafka는 새 Flow의 실제 저장을 확인한 뒤 제거했다.

작성 3 검증을 위해 기존 `python` 플레이어의 서버 확정 이동을 한 번 수행했다.

```text
command_id: 64dc9bd5-75a1-4233-9b0f-6acba7b13b89
event_id: 99f64a9d-860f-44d1-bc42-d6043b054ec0
event_type: player.moved
player_id: 7
room_id: room-3
position: (5, 5)
version: 137
```

기존 publisher가 원본 사건을 `game.events.v1`에 전달한 뒤, 실행 중이지 않던 변환기를 `--max-events 1`로 한 번 실행해 같은 사건을 `game.actions.v1`에 보냈다. 이 일회성 변환기는 종료되어 백그라운드에 남아 있지 않다.

NiFi 저장 결과:

```text
data/nifi/game-actions/4800de5d-6264-4ebc-944d-40f8204e6993
schema_version: 1
event_id: 99f64a9d-860f-44d1-bc42-d6043b054ec0
event_type: player.moved
payload.action_label: 이동
```

`earliest`로 시작해 이 검증 전에 과거 확정 행동 892개도 독립 출력 폴더에 저장됐다. 새 행동을 계속 실시간 수집하려면 다음 명령을 별도 터미널에서 실행한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server\server
.\.venv\Scripts\python.exe manage.py transform_game_actions
```

추가한 계약과 문서:

- `data/contracts/nifi-ingestion-plan.json`
- `docs/server-routing/files/data/contracts/nifi-ingestion-plan.json.md`
- `docs/server-routing/README.md`의 NiFi 수집 계약 색인

계약 파일은 현재 Flow의 토픽·consumer group·처리 방식·출력 경계만 기록하며 인증 정보는 포함하지 않는다.

## 수정된 8교시 작성 2 재적용

수정 교안은 Docker NiFi용 Kafka listener를 29092·29094·29096으로 제시한다. 이전 교안에 맞춰 사용하던 19092·19094·19096을 다음 범위에서 함께 교체했다.

- `infra/kafka/node1.properties`, `node2.properties`, `node3.properties`
- `tools/start-dev.ps1`의 포트 점검 목록
- NiFi Controller Service의 Bootstrap Servers
- 해당 파일의 라우팅 문서와 실행 안내

Controller Service 표시 이름도 교안의 구현 미션에 맞춰 `Village local Kafka · actions read`로 변경했다. Kafka 세 노드만 재시작했으며 Django runserver와 기존 publisher는 유지했다. 적용 후 결과는 다음과 같다.

```text
Kafka KRaft leader: 2
Kafka max follower lag: 0
NiFi -> Kafka TCP 29092/29094/29096: PASS
Controller Service: ENABLED, VALID
ConsumeKafka actions: RUNNING, VALID
```

새 listener로 작성 3을 다시 검증하기 위해 `python` 플레이어를 왼쪽으로 한 칸 이동했다.

```text
command_id: 985da737-ab4d-4fac-94d3-273e720740c9
event_id: b5fd9182-532a-4cfe-aa9f-f9ee252b78d4
event_type: player.moved
player_id: 7
room_id: room-3
position: (4, 5)
version: 138
NiFi file: data/nifi/game-actions/18db37b7-b790-402a-927a-fda22d6db11e
payload.action_label: 이동
```

기존 publisher가 새 사건을 자동 전달한 것을 확인했고 변환기는 다시 `--max-events 1`로 실행한 뒤 종료했다. NiFi 검색 결과는 `matching_files=1`, `scan_truncated=false`였다. 새 행동을 계속 변환하려면 `transform_game_actions`를 별도 터미널에서 지속 실행해야 한다.

수정 교안의 계획 예시에 맞춰 `data/contracts/nifi-ingestion-plan.json`에 `independent_of_spark_checkpoint: true`도 추가했다.

클러스터 검증:

```powershell
cd C:\MLO01-01\nifi-cluster\nifi-compose
docker compose --profile tools run --rm verify
```
