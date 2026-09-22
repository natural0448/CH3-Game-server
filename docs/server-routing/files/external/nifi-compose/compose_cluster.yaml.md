# `C:/MLO01-01/nifi-cluster/nifi-compose/compose_cluster.yaml`

## 책임과 호출 경계

15일차 교안의 Docker 방식으로 ZooKeeper 3노드와 NiFi 2.12.0 3노드를 구성한다. 최초 실행에서 공통 CA, 노드별 인증서, 공통 민감 속성 키와 `admin` 초기 권한을 만들고 이후에는 named volume의 값을 재사용한다. NiFi Flow와 Kafka Processor 자체는 사용자가 NiFi 화면에서 구성한다.

Compose 폴더와 기존 이름을 유지한다. 관리자 비밀번호는 같은 폴더 `.env`의 `NIFI_PASSWORD`, NiFi 출력 경로는 `VILLAGE_LAB_DIR`에서 읽으며 실제 값을 문서나 로그에 복사하지 않는다.

## 서비스와 값의 출처

```text
initialize
  입력: .env의 NIFI_PASSWORD, private와 nifiN-tls named volume.
  호출: /setup/initialize.py.
  메모리: 일회성 컨테이너 상한 384MiB.
  결과: 공통 CA, 서로 다른 노드 인증서·PKCS12 저장소,
        admin 로그인 설정, 공통 sensitive key를 최초 한 번 생성 또는 검증.

zk1, zk2, zk3
  이미지: zookeeper:3.9.5.
  값: ZOO_MY_ID 1~3, 공통 ZOO_SERVERS.
  메모리: 노드당 112MiB, JVM Xms 32MiB·Xmx 64MiB.
  결과: healthcheck를 통과한 세 노드 ensemble.

nifi1, nifi2, nifi3
  이미지: apache/nifi:2.12.0.
  입력: initialize 결과와 ZooKeeper healthcheck.
  호출: /setup/start-node.py 후 /opt/nifi/scripts/start.sh.
  결과: HTTPS 8443, cluster protocol 11443, 노드별 상태·저장소 volume.
  메모리: 노드당 832MiB, JVM heap init 128MiB·max 448MiB.
  CPU: 노드당 최대 2개를 사용해 NAR 로드·Flow 실행·웹 요청을 병렬 처리.
  클러스터 응답 제한: nifi.cluster.node.read.timeout=30 sec.
  호스트 주소: localhost:8443, 8444, 8445.
  Kafka 호스트 별칭: host.docker.internal.
  출력: VILLAGE_LAB_DIR/data/nifi/game-actions를 /work/output에 mount.

verify (tools profile)
  입력: private volume의 저장된 인증 정보와 CA.
  호출: /setup/verify.py.
  결과: 세 URL 로그인, CONNECTED 3노드, heartbeat 진행을 검증한 비밀값 없는 JSON.
```

지속 실행되는 NiFi 3개와 ZooKeeper 3개의 컨테이너 메모리 상한 합계는 2832MiB다. 사용자 `.wslconfig`가 Docker의 WSL VM을 4GB로 제한하므로 약 1.2GiB를 Docker daemon, Linux page cache와 컨테이너 native memory에 남긴다. NiFi는 초기 heap을 낮추되 노드당 CPU 상한을 2개로 높여 유휴 메모리를 줄이고 작업 중 CPU 병렬 처리를 허용한다. `initialize`와 `verify`는 일회성 작업이며 지속 실행 합계에 포함하지 않는다.

## 볼륨 경계

Compose가 이름을 선언해 보존하는 볼륨은 교안 구성과 같은 31개다.

```text
private 1개
ZooKeeper data/datalog 6개
NiFi 노드별 tls/conf/state/database/flowfile/content/provenance/logs 24개
```

`private`는 초기화 컨테이너를 지운 뒤 Docker에서 미참조로 표시될 수 있지만 CA·개인키·관리자 설정을 가진 필수 볼륨이므로 삭제하지 않는다. 실행 중인 공식 이미지가 자동으로 만드는 익명 볼륨은 ZooKeeper `/logs` 3개와 NiFi `nar_extensions`·`python_extensions` 6개다. 이 9개는 Compose의 영구 데이터 설계에 추가한 볼륨이 아니며 현재 사용량은 모두 0B다. 컨테이너 실행 중에는 삭제할 수 없고 같은 공식 이미지로 다시 만들면 자동 생성된다.

일회성 `initialize`가 종료된 뒤에는 해당 컨테이너를 `docker rm -v`로 제거해 그 컨테이너 전용 익명 볼륨 9개를 함께 정리한다. `docker volume prune`은 필수 `private`까지 삭제할 수 있으므로 사용하지 않는다.

```powershell
docker compose --env-file .env -f compose_cluster.yaml rm -f -v initialize
```

## 포함 Python 진입점

### `initialize.py`의 `run(*args) -> bytes`

```text
subprocess.run으로 인증서 명령 실행
표준 출력·오류를 내부에서 수집
실패하면 명령 이름만 포함한 RuntimeError
성공하면 stdout 반환
```

직접 호출: `openssl`, `keytool`.

### `initialize.py`의 `write(path, value) -> None`

```text
같은 디렉터리의 pending 파일에 0600 권한으로 기록
원래 경로로 원자적 교체
```

### `start-node.py`의 `read_properties() -> dict[str, str]`

```text
현재 nifi.properties 읽기
주석과 빈 줄 제외
첫 등호를 기준으로 key/value 반환
```

### `start-node.py`의 `set_property(name: str, value: str) -> None`

```text
nifi.properties를 줄 단위로 읽음
name과 같은 기존 항목은 첫 항목만 name=value로 교체
항목이 없으면 마지막에 name=value 추가
결과가 달라진 경우에만 파일을 다시 기록
```

직접 적용하는 값은 `nifi.cluster.node.read.timeout=30 sec`다. 재시작 직후 `/nifi-api/flow/processor-types`의 첫 확장 목록 생성이 기본 5초를 넘을 수 있어 클러스터 내부 요청이 중간에 끊기지 않도록 한다. 일반 웹 요청 제한 60초와 연결 timeout 5초는 유지한다.

이 진입점은 최초 노드 conf에 다음 권한 관계를 쓴다.

```text
file-user-group-provider
  Initial User Identity: admin, CN=nifi1, CN=nifi2, CN=nifi3.

file-access-policy-provider
  Initial Admin Identity: admin.
  Node Identity: CN=nifi1, CN=nifi2, CN=nifi3.

managed-authorizer
  Access Policy Provider: file-access-policy-provider.

single-user-provider
  admin의 .env 비밀번호 로그인을 처리한다.
```

이미 `users.xml`, `authorizations.xml`, flow 파일 또는 다른 sensitive key가 있는 미관리 conf는 자동 초기화하지 않고 중단한다.

### `verify.py`의 `request(url, data=None, token=None) -> bytes`

```text
공통 CA로 HTTPS 서버 이름 검증
필요할 때만 form 또는 Bearer header 구성
응답 본문 bytes 반환
비밀번호와 access token은 출력하지 않음
```

### `verify.py`의 `snapshot() -> list[dict]`

```text
nifi1~nifi3 각각에서 admin token 발급
/nifi-api/controller/cluster 조회
노드 3개가 모두 CONNECTED인지 검사
주소·API 포트·상태·역할·heartbeat만 반환
```

## 실행 관계

```text
docker compose up
  initialize 완료 대기
  ZooKeeper healthcheck 대기
  NiFi 세 노드 시작
  각 NiFi healthcheck가 공통 CA로 자기 HTTPS 확인

docker compose --profile tools run --rm verify
  실행 중인 세 노드에 admin으로 로그인
  cluster 상태를 두 번 읽고 heartbeat 진행 확인
```
