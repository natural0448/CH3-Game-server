# `tools/start-dev.ps1`

## 책임과 호출 경계

`without-nifi`와 `with-nifi` 두 프로필 중 하나로 로컬 인프라를 실행한다. `without-nifi`는 Kafka 3노드와 Spark Master·Worker 2개를, `with-nifi`는 Kafka 3노드와 Spark Master·Worker 1개 및 Docker Compose의 ZooKeeper 3개·NiFi 3개를 각각 별도 PowerShell 창에서 실행한다. Django, publisher, Spark 작업 제출, Kafka 토픽 관리와 NiFi Flow 구성은 호출하지 않는다.

Docker Compose 파일과 `.env`는 외부 인프라 경로 `C:/MLO01-01/nifi-cluster/nifi-compose`가 소유한다. 실행기는 값을 생성하거나 출력하지 않고 구성 유효성만 검사한다.

## 파라미터

```text
Profile: with-nifi | without-nifi
  기본값 without-nifi.
  without-nifi는 Kafka 3개와 Spark Master·Worker 1·2를 연다.
  with-nifi는 Kafka 3개와 Spark Master·Worker 1 및 Docker NiFi·ZooKeeper를 연다.

ChildService: kafka1 | kafka2 | kafka3 | spark-master | spark-worker1 | spark-worker2 | nifi
  기본값 없음. 프로필 실행기가 서비스별 별도 창을 만들 때 내부적으로 전달한다.
  일반 실행에서는 직접 지정하지 않는다.

CheckOnly: switch
  파일·포트·Docker Engine·Compose 설정만 검사하고 프로세스를 시작하지 않는다.

DockerCliPath: string
  docker.exe의 명시 경로다. 기본 출처는 DOCKER_CLI 환경 변수다.
```

## 주요 변수와 상수

```text
projectRoot
  출처: 스크립트 부모 폴더의 부모. Game-server 루트다.

sparkRoot
  값: C:/MLO01-01/Chapter3/Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1.

bundledJavaHome / bundledJavaPath
  값: PROJECT_ROOT/infra/runtime/temurin-jdk21/jdk-21.0.12.1+1과 그 아래 bin/java.exe.
  프로젝트 Java를 우선 사용하며 선택한 경로는 현재 실행기와 자식 창에만 JAVA_HOME·PATH로 전달한다.

nifiComposeRoot
  값: C:/MLO01-01/nifi-cluster/nifi-compose.

nifiComposeFile
  값: nifiComposeRoot/compose_cluster.yaml.

servicePorts
  Kafka 호스트 client/controller: 9092~9097.
  Kafka Docker bridge client: 29092, 29094, 29096.
  Spark: Master 7077·8080, Worker 1은 7078·8081, Worker 2는 7079·8082.
  Docker NiFi: 호스트 HTTPS 8443~8445.

dockerCli
  DockerCliPath, PATH, Docker Desktop의 시스템·사용자 설치 경로와 일반 도구 경로에서 찾은 docker.exe다.

nifiPreflightIssues
  Docker CLI·Engine·Compose v2, Compose 파일 유효성,
  initialize·zk1~3·nifi1~3 서비스 존재 여부의 검사 결과다.
```

### `Initialize-JavaRuntime() -> string`

```text
프로젝트에 포함된 Java 21을 첫 후보로 확인
없으면 현재 JAVA_HOME/bin/java.exe와 PATH의 java.exe를 순서대로 확인
선택한 java.exe의 상위 경로를 현재 프로세스 JAVA_HOME으로 설정
현재 프로세스 PATH에 Java bin이 없으면 앞에 추가
선택한 java.exe 절대경로 반환
후보가 모두 없으면 예상 프로젝트 경로를 포함한 예외 발생
```

전역·사용자 환경 변수는 수정하지 않으며 별도 PowerShell 서비스 창은 이 프로세스 환경을 상속한다.

## 함수

### `Test-Listening([int]$Port) -> bool`

```text
운영체제의 활성 TCP listener 목록 조회
Port와 같은 listener가 하나라도 있으면 true
없거나 listener 조회가 실패하면 false
```

직접 호출: `.NET System.Net.NetworkInformation.IPGlobalProperties.GetActiveTcpListeners()`.

### `Test-ServicePortInUse([string]$Name) -> bool`

```text
servicePorts[Name] 순회
Test-Listening 호출
하나라도 사용 중이면 안내 후 true
전부 비어 있으면 false
```

### `Resolve-DockerCli() -> string|null`

```text
DockerCliPath와 PATH 확인
Docker Desktop의 Program Files·사용자 설치 경로 확인
일반 사용자·Chocolatey 설치 경로 확인
첫 번째 실제 docker.exe 절대경로 반환
없으면 null
```

### `Invoke-Docker([string]$DockerCli, [string[]]$Arguments) -> hashtable`

```text
DockerCli를 Arguments와 함께 실행
Windows PowerShell의 native stderr 처리 중단을 방지
Docker 실행 자체가 거부되거나 실패하면 예외를 사전 검사 결과로 변환
ExitCode와 Output 배열 반환
```

직접 호출: 선택된 `docker.exe`.

### `Get-NifiPreflightIssues([string]$DockerCli) -> string[]`

```text
compose_cluster.yaml 존재 확인
Docker CLI와 Engine 응답 확인
Docker Compose v2 확인
docker compose config --quiet로 .env 포함 구성 검증
config --services에서 initialize·zk1~3·nifi1~3 확인
발견한 문제 목록 반환
```

구성 내용과 `.env` 값은 출력하지 않는다.

### `Confirm-Files([bool]$IncludeNifi, [string]$JavaPath) -> void`

```text
선택된 JavaPath와 Spark 실행 파일·jars 확인
Kafka 실행기·노드 설정·데이터 메타·라이브러리 확인
IncludeNifi가 true일 때만 외부 NiFi compose_cluster.yaml 확인
누락 시 예외
```

## 최상위 실행 흐름

```text
Profile 또는 ChildService 이름으로 체크아웃별 mutex 획득
Initialize-JavaRuntime으로 프로젝트 Java 우선 선택
Confirm-Files(IncludeNifi, JavaPath)
Profile이 with-nifi이거나 ChildService가 nifi일 때만 Docker CLI 탐색과 NiFi Compose 사전 검사

if CheckOnly:
    without-nifi이면 Kafka 3개·Spark Master·Worker 1·2 포트 확인
    with-nifi이면 Kafka 3개·Spark Master·Worker 1과 NiFi 포트·Docker Compose 확인
    ChildService이면 해당 서비스 포트만 확인
    프로세스 없이 종료

if ChildService가 없음:
    without-nifi이면 Kafka 3개·Spark Master·Worker 1·2 목록 구성
    with-nifi이면 Kafka 3개·Spark Master·Worker 1·NiFi 목록 구성
    NiFi 사전 검사 실패 시 NiFi만 건너뜀
    이미 포트가 열렸으면 해당 서비스 건너뜀
    나머지는 ChildService를 지정한 별도 PowerShell 창으로 이 스크립트를 재호출

if ChildService가 Kafka:
    tools/kafka.ps1 -Action start -Node 호출
elif ChildService가 Spark:
    SPARK_DAEMON_MEMORY를 192m으로 제한
    spark-class.cmd로 Master 또는 Worker 전경 실행
    Worker 번호로 서비스 포트(7077+번호), 웹 포트(8080+번호), work/worker-번호 경로 계산
    Worker는 각각 4코어·실행 메모리 768m로 등록
else ChildService가 nifi:
    Docker Compose 사전 검사 재확인
    compose_cluster.yaml을 docker compose up으로 전경 실행

종료 시 mutex 해제
```

외부 호출 결과 기대:

- `tools/kafka.ps1`: 선택 Kafka 노드를 현재 창에서 실행한다.
- `spark-class.cmd`: Spark 프로세스가 현재 창을 소유한다.
- `docker compose up`: ZooKeeper 3개·NiFi 3개 로그를 한 창에 연결하고 `Ctrl+C`로 중단할 수 있게 한다.
