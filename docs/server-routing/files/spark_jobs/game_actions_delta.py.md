# `spark_jobs/game_actions_delta.py`

## 책임과 호출 경계

`game.actions.v1`을 Structured Streaming으로 읽어 `event_id` 기준 고유 사실을 Delta에 저장한다. 최초 배치는 Delta 테이블을 만들고, 이후 배치는 `incoming_actions` 임시 뷰와 `MERGE`를 사용한다. Django 제출 계층에서 Kafka 주소·데이터 경로·진행 파일 경로를 인자로 받는다.

## 함수

### `main() -> None`

```text
명령행에서 data-dir, Kafka 주소, topic, progress 출력 경로를 읽음
Delta 확장과 Asia/Seoul 시간대를 사용하는 SparkSession 생성
Kafka value를 공통 사건 필드와 원문·payload·Kafka 위치로 변환
schema_version 1과 세 행동 종류만 선택
save_unique를 foreachBatch callback으로 등록
5초마다 실행하고 새 batch 진행 상태를 JSON으로 교체 게시
Ctrl+C 또는 실패 시 query와 SparkSession 종료
```

직접 호출: Spark Kafka source, Spark Structured Streaming, Delta sink, `Path.replace`.

### `save_unique(batch, batch_id) -> None`

- `batch`: 현재 micro-batch의 행동 DataFrame.
- `batch_id`: Spark가 부여한 현재 micro-batch 번호.

```text
event_id 중복 제거
빈 배치면 반환
DataFrame cache
Delta 로그가 없으면 최초 Delta 테이블 저장
Delta 로그가 있으면 incoming_actions 임시 뷰 생성
foreachBatch가 전달한 batch DataFrame의 SparkSession으로 MERGE 실행
saved.event_id와 incoming.event_id가 일치하지 않는 행만 INSERT
처리 건수 출력
항상 cache 해제
```

## 주요 변수와 값 출처

- `data_dir`: `--data-dir`을 절대 경로로 변환한 데이터 루트.
- `target`: `<data-dir>/lake/silver/game_actions`에서 `Path.as_uri()`로 만든 file URI 문자열.
- `spark`: `main`이 만든 driver SparkSession.
- `actions`: `game.actions.v1`에서 허용 행동만 남긴 streaming DataFrame.
- `batch`: foreachBatch가 전달한 현재 micro-batch DataFrame이며 MERGE SQL의 SparkSession 출처.
- `checkpoint`: `<data-dir>/checkpoints/game-actions-delta-v1`.
- `progress_path`: 명시된 `--progress-output` 또는 `<data-dir>/marts/progress-game-actions.json`.
