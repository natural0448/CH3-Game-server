# `tools/kafka.ps1`

## 책임과 호출 경계

로컬 Kafka 4.1.2 KRaft 3노드의 최초 포맷, 단일 노드 실행, quorum 상태, 수업 토픽과 consumer group 조회를 담당한다. 데이터 디렉터리를 삭제하거나 다른 cluster ID로 다시 포맷하지 않는다.

## 파라미터

```text
Action
  init | start | status | create-topic | describe-topic | group.
  기본값 status.

Node
  1..3. start에서 실행할 노드 번호이며 기본값 1.

Group
  group 조회에 사용할 consumer group. 기본값 village-watch-v1.
```

## 주요 변수와 값의 출처

```text
projectRoot
  출처: tools 폴더의 부모. Game-server 루트.

runtimePath
  값: PROJECT_ROOT/infra/runtime/kafka_2.13-4.1.2.

dataPath
  값: PROJECT_ROOT/data/kafka.

manifestPath
  값: data/kafka/cluster.json. 최초 생성한 cluster ID와 controller voter ID의 출처.

bootstrap
  값: 127.0.0.1:9092,127.0.0.1:9094,127.0.0.1:9096.

javaPath
  우선 출처: PROJECT_ROOT/infra/runtime/temurin-jdk21/jdk-21.0.12.1+1/bin/java.exe.
  대체 출처: 현재 JAVA_HOME/bin/java.exe, PATH의 java.exe 순서다.
  선택한 Java의 JAVA_HOME·bin PATH는 현재 PowerShell 프로세스에만 설정한다.

Kafka JVM heap
  값: Xms 96m, Xmx 320m. 관리 도구와 각 broker/controller 프로세스에 적용.

Kafka direct memory
  값: MaxDirectMemorySize 128m. 네트워크·파일 버퍼의 JVM 외 확장 상한.
```

## 함수

### `Initialize-JavaRuntime() -> string`

```text
프로젝트 Java 21, 현재 JAVA_HOME, PATH의 java.exe 순서로 후보 확인
첫 실제 java.exe의 절대경로 반환
현재 프로세스 JAVA_HOME과 PATH를 선택한 Java에 맞춤
후보가 모두 없으면 프로젝트 Java 예상 경로와 함께 예외
```

전역·사용자 환경 변수는 수정하지 않는다.

### `Invoke-KafkaJava([string]$Class, [string[]]$Arguments) -> void`

```text
Kafka tools용 log4j2 설정, 96m..320m heap과 direct memory 128m 구성
runtime libs를 classpath로 지정
Class와 Arguments로 java 실행
종료 코드가 0이 아니면 예외
```

직접 호출: `Initialize-JavaRuntime`이 선택한 `javaPath`, Kafka 도구 클래스.

## 최상위 실행 흐름

```text
스크립트 시작:
    Initialize-JavaRuntime으로 프로젝트 Java 21을 우선 선택

Action == init:
    기존 cluster manifest가 있으면 재사용
    없으면 각 노드 데이터가 비어 있는지 확인하고 cluster/controller UUID 생성
    각 노드 meta.properties가 같은 cluster와 node인지 확인
    미포맷 노드만 StorageTool format

Action == start:
    선택 노드 meta.properties 확인
    선택 노드 아래 Windows ReadOnly 파일 속성만 해제
    Kafka 데이터나 checkpoint 내용은 삭제하지 않음
    노드별 로그 폴더 생성
    96m..320m heap과 direct memory 128m으로 kafka.Kafka 전경 실행

Action == status:
    MetadataQuorumCommand로 3노드 quorum 상태 조회

Action == create-topic:
    game.events.v1을 partition 3, replication factor 3, min ISR 2로 생성

Action == describe-topic:
    game.events.v1 배치와 ISR 조회

Action == group:
    Group 값의 consumer offset과 lag 조회
```

Windows의 Kafka recovery checkpoint가 `ReadOnly` 속성을 가진 채 남으면 Kafka가 `.deleted` 파일을 정리하지 못하고 시작할 수 있다. `start`는 선택 노드의 파일 내용이나 이름을 바꾸지 않고 이 속성만 해제한 뒤 broker를 실행한다.
