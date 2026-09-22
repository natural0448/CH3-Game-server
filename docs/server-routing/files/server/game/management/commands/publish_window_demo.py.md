# `server/game/management/commands/publish_window_demo.py`

## 책임과 호출 경계

운영 게임에서 소비하지 않는 별도 Kafka 토픽에 시간 창 실습용 합성 사건을 결정적인 순서로 발행한다. 실제 게임 상태, Django 모델, 운영 행동 토픽과 Spark 작업은 수정하거나 실행하지 않는다.

## 상수와 값의 출처

```text
topic
  값: game.actions.window-demo.v1.

phases
  값: 1~5 단계별 (event 번호, 기준 시각 이후 초) 목록.
  단계 1=(1,2),(2,4), 단계 2=(3,12),(4,14), 단계 3=(5,25),
  단계 4=(6,45), 단계 5=(7,65).

base
  값: 2026-09-11T01:00:00+00:00.

Kafka bootstrap servers
  출처: settings.KAFKA_BOOTSTRAP_SERVERS.
```

## 클래스와 메서드

### `Command.add_arguments(self, parser) -> None`

파라미터:

```text
parser
  Django 관리 명령 argument parser.
```

의사코드:

```text
필수 --phase 정수 인자 등록
허용 범위를 1..5로 제한
```

직접 호출: Django argument parser의 `add_argument`.

### `Command.handle(self, *args, **options) -> None`

파라미터:

```text
args
  Django가 전달하는 추가 위치 인자.

options
  phase: 필수 정수 1..5.
```

의사코드:

```text
KafkaAdminClient 생성
별도 demo topic을 partition 1, replication factor 3, min ISR 2로 생성 시도
이미 있으면 계속하고 admin 닫기
선택 phase의 결정적 사건 목록 순회
base와 초 오프셋으로 event_time 생성
고정 player_id 999와 demo-room을 가진 schema version 1 사건 구성
KafkaProducer로 key 999와 JSON 값을 acks=all로 전송하고 최대 10초 대기
phase, topic, partition, offset, event_time만 표준 출력
producer 닫기
```

직접 호출:

- `KafkaAdminClient`, `NewTopic`: 별도 실습 토픽이 존재하도록 보장한다.
- `KafkaProducer`: 합성 JSON 사건을 발행하고 broker 응답 메타데이터를 받는다.
- `UUID`, `datetime`, `timedelta`: 재실행해도 같은 실습 식별자와 사건 시각을 만든다.
- `self.stdout.write`: 인증 정보 없이 발행 위치와 시각을 출력한다.
