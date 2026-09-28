# `infra/kafka/node1.properties`

## 책임과 호출 경계

Kafka 1번 프로세스를 broker와 KRaft controller로 실행하는 속성 파일이다. 호스트 프로그램은 `PLAINTEXT` listener를, Docker bridge의 NiFi는 `DOCKER` listener를 사용한다. 토픽 생성이나 소비자 설정은 이 파일이 담당하지 않는다.

## 속성

```text
process.roles = broker,controller
node.id = 1
controller.quorum.bootstrap.servers
  출처: 같은 PC의 세 controller 주소 127.0.0.1:9093,9095,9097.

listeners
  PLAINTEXT: 127.0.0.1:9092
  DOCKER: 모든 호스트 인터페이스의 29092
  CONTROLLER: 127.0.0.1:9093

advertised.listeners
  PLAINTEXT: 호스트 클라이언트용 127.0.0.1:9092
  DOCKER: NiFi 컨테이너용 host.docker.internal:29092

listener.security.protocol.map
  PLAINTEXT·DOCKER·CONTROLLER를 수업용 평문 전송으로 연결한다.

inter.broker.listener.name = PLAINTEXT
controller.listener.names = CONTROLLER
log.dirs = C:/MLO01-01/Chapter3/Game-server/data/kafka/node1
log.cleaner.enable = false
  Windows가 memory-mapped compacted index의 rename을 막아 log dir을 실패 처리하는 것을 방지한다.

log.retention.ms = -1
  수업용 Windows 실행 중 보존기간 만료 세그먼트의 index rename·삭제를 수행하지 않는다.
```

복제 기본값은 3, 최소 ISR은 2이며 자동 토픽 생성, 로컬 log cleaner, 실행 중 보존기간 삭제를 끈다. 토픽 기록과 consumer offset 기록은 유지된다. 수업 데이터가 자동 삭제되지 않으므로 디스크 정리는 Kafka 세 노드를 모두 정상 종료한 상태에서 별도 백업·초기화 절차로 수행한다. `tools/kafka.ps1 -Action start -Node 1`이 이 파일을 Kafka 프로세스에 직접 전달한다.
