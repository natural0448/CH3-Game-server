# 교육용 상시 인프라 메모리·CPU 최적화 인수인계

## 요청 목적과 완료 결과

Kafka 3노드, Spark, NiFi 3노드를 수업 중 함께 유지하면서 Windows 메모리 압력을 낮추고 16개 논리 CPU를 더 사용할 수 있게 조정했다. 기본 `start-dev.cmd`는 Kafka 3노드, Spark Master·Worker 1개, Docker ZooKeeper 3노드·NiFi 3노드를 실행한다. Spark Worker 2는 기본 실행에서 제외하고 명시 실행만 허용한다.

작업 종료 시 Kafka 3노드, Spark Master·Worker 1개, NiFi 3노드와 ZooKeeper 3노드는 모두 실행 중이다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `e24b87e 15day - 6교시`
- staged 변경: 없음
- 작업 시작 전에 이미 존재한 수정: 서버 라우팅 색인, Kafka node 설정 3개, Spark 제출 관리 명령 3개, `tools/start-dev.ps1`, `한번에_실행.md`
- 작업 시작 전에 이미 존재한 untracked: 15·16일차 handoff와 라우팅 문서, `run_game_windows.py`, `game_windows.py`, `publish_window_demo.py`, `find_nifi_event.py`

기존 변경을 사용자 작업으로 취급해 되돌리지 않았으며 이번 요청과 직접 관련된 파일의 현재 값만 추가 수정했다. 비밀값과 `.env` 값은 문서와 출력에 복사하지 않았다.

## 이번 작업 파일

수정:

- `tools/start-dev.ps1`
- `tools/kafka.ps1`
- `infra/kafka/node1.properties`
- `infra/kafka/node2.properties`
- `infra/kafka/node3.properties`
- `spark_jobs/game_windows.py`
- `server/analytics/management/commands/run_game_windows.py`
- `한번에_실행.md`
- `docs/server-routing/README.md`
- 위 파일들의 기존 짝 라우팅 문서
- 외부 `C:/MLO01-01/nifi-cluster/nifi-compose/compose_cluster.yaml`
- 외부 `C:/MLO01-01/Chapter3/Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1/conf/spark-env.cmd`
- 외부 `C:/MLO01-01/Chapter3/Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1/conf/spark-defaults.conf`
- 외부 `C:/Users/이해나/.wslconfig`

추가:

- `docs/server-routing/files/tools/kafka.ps1.md`
- 이 인수인계 문서

삭제·이동한 파일과 Docker volume은 없다. Compose 컨테이너는 새 자원 제한 적용을 위해 재생성했으며 named volume을 그대로 재사용했다.

## 자원과 책임 경계

- 장비 기준: 물리 RAM 15.36GiB, 논리 CPU 16개.
- Kafka: 3노드 KRaft를 유지하고 노드당 JVM heap 96~320MiB, direct memory 최대 128MiB를 사용한다.
- Spark: 기본 Worker 1개, 4코어·768MiB. Master·Worker daemon은 각각 192MiB, 기본 driver·executor는 각각 768MiB, 기본 병렬도·shuffle partition은 4다.
- NiFi: 3노드를 유지하고 노드당 컨테이너 832MiB, JVM heap 128~448MiB, CPU 최대 2개를 사용한다.
- ZooKeeper: 3노드를 유지하고 노드당 컨테이너 112MiB, JVM heap 32~64MiB를 사용한다.
- WSL: memory 3500MB, swap 1GB, gradual memory reclaim을 사용한다.
- 지속 컨테이너 메모리 상한 합계는 2832MiB다. NiFi·ZooKeeper는 `restart: unless-stopped`를 유지한다.

Spark Worker를 2개에서 1개로 줄여 executor 메모리 중복을 없앴고 Worker 하나의 코어를 2개에서 4개로 높였다. NiFi는 노드 수를 줄이지 않고 노드당 CPU 상한을 1개에서 2개로 높였다. 세 노드 복제·클러스터 수업 계약은 유지한다.

## Windows Kafka 안정화

실제 동시 기동 중 Kafka 4.1.2가 Windows에서 다음 두 문제로 종료되는 것을 확인했다.

1. recovery checkpoint의 `ReadOnly` 속성 때문에 `.deleted` 파일 삭제가 거부됨
2. compacted `__consumer_offsets`의 memory-mapped index rename이 Windows 파일 잠금과 충돌함

`tools/kafka.ps1`은 시작할 노드 아래 파일의 `ReadOnly` 속성만 해제한다. 파일 내용과 이름은 삭제하거나 변경하지 않는다. 세 node 설정에는 로컬 수업용 `log.cleaner.enable=false`를 적용했다. 복제와 consumer offset 기록은 계속되지만 자동 log compaction은 수행하지 않으므로 장기 운영 환경이 아닌 수업 데이터에만 사용하는 설정이다.

## 라우팅 문서 정합화

- `tools/kafka.ps1`의 새 짝 문서를 만들고 서버 라우팅 색인에 추가했다.
- `tools/start-dev.ps1`, Kafka node 3개, `game_windows.py`, `run_game_windows.py`의 짝 문서를 현재 구현과 맞췄다.
- 외부 NiFi Compose, Spark env/defaults, `.wslconfig`의 짝 문서를 실제 자원값과 맞췄다.
- 추가·이동·삭제가 없는 다른 개발 파일의 문서는 수정하지 않았다.

## 검사 결과

- PowerShell parser: `tools/start-dev.ps1`, `tools/kafka.ps1` 통과
- Python compile: `spark_jobs/game_windows.py`, `run_game_windows.py` 통과
- Django `manage.py check`: 문제 없음
- Docker Compose `config --quiet`: 통과
- Kafka quorum: voter 3개, leader 1, follower lag 0
- Spark Master JSON: Worker `ALIVE`, 4 cores, 768MiB
- NiFi verify: TLS·세 노드 로그인 통과, `CONNECTED=3`, heartbeat 진행
- Docker 실제 제한: NiFi 832MiB·2 CPU·unless-stopped, ZooKeeper 112MiB·unless-stopped
- 최종 측정 컨테이너 메모리: NiFi 노드당 약 593~605MiB, ZooKeeper 노드당 약 62~72MiB
- 최종 측정 네이티브 JVM: Kafka 노드당 약 244~258MiB, Spark Master·Worker daemon 약 211MiB·206MiB
- WSL 변경 전/후: `VmmemWSL` 약 4.0GiB → 3.37GiB
- Kafka·Spark·NiFi를 모두 실행한 최종 Windows 가용 RAM: 약 2.05GiB. 이전 전체 구성 측정 약 1.68GiB보다 약 0.37GiB 증가

## Spark Master `disassociated` 로그 조치

Spark Master와 Worker 상태를 확인한 결과 Worker는 `ALIVE`, 4 cores, 768MiB로 정상 등록되어 있었다. Master 로그의 `got disassociated, removing it`은 Worker 종료가 아니라 `tools/start-dev.ps1`의 기존 포트 검사가 7077 포트에 짧은 TCP 연결을 만들고 즉시 닫을 때 남은 기록이었다.

`Test-Listening`을 실제 TCP 접속 대신 운영체제의 활성 listener 목록을 읽는 방식으로 변경했다. 이에 따라 `-CheckOnly` 및 중복 실행 검사는 Spark RPC 연결을 만들지 않으며, Kafka·Spark·NiFi 프로세스의 실행 상태에도 영향을 주지 않는다.

이 후속 조치를 시작할 때 HEAD는 `e24b87e`였고 staged 변경은 없었다. 작업 시작 전에 존재한 여러 변경 중 `tools/start-dev.ps1`과 해당 라우팅 문서·이 인수인계 문서만 이번 원인에 맞게 추가 수정했으며, 나머지 변경은 건드리지 않았다.

후속 검증:

- PowerShell parser: 통과
- `tools/start-dev.ps1 -Service day16 -CheckOnly`: 서비스 추가 실행 없이 통과
- CheckOnly 전후 7077 연결 수: 증가 없음
- Spark Master JSON: Master `ALIVE`, Worker 1개 `ALIVE`, 4 cores, 768MiB
- `git diff --check`: 통과

## 남은 위험과 운영 기준

- NiFi 현재 사용량이 700MiB를 넘으므로 컨테이너 상한을 768MiB 이하로 더 낮추면 NAR 로드나 repository 작업 중 OOM 위험이 크다.
- Kafka log cleaner를 끈 상태에서는 compacted topic 파일이 장기간 누적된다. 수업 데이터 규모에서는 허용하지만 디스크 사용량을 주기적으로 확인한다.
- Spark 작업을 여러 개 동시에 제출하면 각 driver·executor 메모리가 추가된다. 메모리가 부족할 때는 streaming query를 하나씩 실행한다.
- Windows Kafka·Spark는 해당 PowerShell 창이 열려 있는 동안 유지된다. Docker NiFi·ZooKeeper는 Docker Desktop이 실행 중이면 `restart: unless-stopped` 정책으로 복구된다.

## 다음 실행과 확인 순서

전체 인프라가 꺼진 경우 Docker Desktop이 준비된 뒤 다음 명령 하나를 사용한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\start-dev.cmd
```

상태 확인:

```powershell
.\tools\kafka.ps1 -Action status
Invoke-RestMethod http://127.0.0.1:8080/json/
docker compose --project-directory C:\MLO01-01\nifi-cluster\nifi-compose `
  --env-file C:\MLO01-01\nifi-cluster\nifi-compose\.env `
  -f C:\MLO01-01\nifi-cluster\nifi-compose\compose_cluster.yaml ps
```

Spark Worker 2가 특별히 필요한 교시에서만 다음 명령을 추가한다.

```powershell
.\start-dev.cmd -Service spark-worker2
```
