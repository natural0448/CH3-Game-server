# `server/analytics/management/commands/collect_game_metrics.py`

## 책임과 실행 경계

최근 MySQL 확정 사실, publisher 발행 표시, Python 행동 변환기 Kafka group 위치와 기존 Spark progress 파일을 하나의 읽기 전용 운영 snapshot으로 게시한다. Kafka 메시지를 poll·commit하지 않고 Spark 작업도 시작하지 않는다. 출력은 `settings.DATA_DIR/marts/game-metrics.json`에 원자적으로 교체한다.

## 클래스와 메서드

### `Command.add_arguments(self, parser) -> None`

- `--seconds`: 최근 DB 관찰 구간, 기본 60, 허용 1..3600초.
- `--topic`: Kafka metadata를 읽을 입력 topic, 기본 `game.events.v1`.
- `--group`: committed offset을 읽을 Python 변환기 group, 기본 `village-actions-v1`.

### `Command.handle(self, *args, **options) -> None`

```text
seconds 범위 검사 후 동일한 now로 window_start/window_end 계산
Kafka topic partition의 beginning/end/committed offset 조회
retention 범위 안의 partition만 lag 계산하고 consumer를 commit 없이 종료
event_time 구간의 GameEvent 수와 행동·방별 count 계산
published_at 구간 수와 전체 pending 표시 수·가장 오래된 표시 나이 계산
기존 progress-game-actions.json이 있으면 허용된 Spark 진행 필드만 복사
game-metrics.json.tmp에 JSON 작성 후 game-metrics.json으로 교체
동일 report를 표준 출력
```

직접 호출: `KafkaConsumer`, `TopicPartition`, Django `GameEvent` QuerySet, `Count`, `timezone.now`, `Path.read_text/write_text/replace`.

## 주요 변수와 출처

- `partitions`: Kafka metadata와 지정 group의 저장 위치에서 만든 partition별 목록.
- `recent`: `[cutoff, now)`의 `GameEvent` QuerySet.
- `pending`: `published_at IS NULL`인 전체 행.
- `spark_progress`: 기존 Delta streaming driver가 쓴 progress 파일의 허용 필드 또는 `None`.
- `known_lags`: 위치를 확인할 수 있는 partition의 lag만 모은 목록.
- `report`: schema version 1 운영 snapshot. `generated_at`과 Spark `timestamp`를 별도로 유지한다.
