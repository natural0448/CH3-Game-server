# `infra/kafka/node3.properties`

## 책임과 호출 경계

Kafka 3번 프로세스를 broker와 KRaft controller로 실행하는 속성 파일이다. 호스트 프로그램은 `PLAINTEXT` listener를, Docker bridge의 NiFi는 `DOCKER` listener를 사용한다. 토픽 생성이나 소비자 설정은 이 파일이 담당하지 않는다.

## 속성

```text
process.roles = broker,controller
node.id = 3
controller.quorum.bootstrap.servers
  출처: 같은 PC의 세 controller 주소 127.0.0.1:9093,9095,9097.

listeners
  PLAINTEXT: 127.0.0.1:9096
  DOCKER: 모든 호스트 인터페이스의 29096
  CONTROLLER: 127.0.0.1:9097

advertised.listeners
  PLAINTEXT: 호스트 클라이언트용 127.0.0.1:9096
  DOCKER: NiFi 컨테이너용 host.docker.internal:29096

listener.security.protocol.map
  PLAINTEXT·DOCKER·CONTROLLER를 수업용 평문 전송으로 연결한다.

inter.broker.listener.name = PLAINTEXT
controller.listener.names = CONTROLLER
log.dirs = C:/MLO01-01/Chapter3/Game-server/data/kafka/node3
log.cleaner.enable = false
  Windows가 memory-mapped compacted index의 rename을 막아 log dir을 실패 처리하는 것을 방지한다.
```

복제 기본값은 3, 최소 ISR은 2이며 자동 토픽 생성과 로컬 log cleaner를 끈다. 토픽 기록과 consumer offset 기록은 유지되며 수업 데이터는 자동 compact하지 않는다. `tools/kafka.ps1 -Action start -Node 3`이 이 파일을 Kafka 프로세스에 직접 전달한다.
