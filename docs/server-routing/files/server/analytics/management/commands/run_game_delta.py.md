# `server/analytics/management/commands/run_game_delta.py`

## 책임과 호출 경계

Django 설정에서 Spark·Kafka 연결값을 읽고 `spark_jobs/game_actions_delta.py`를 기존 Spark 클러스터에 제출한다. Delta 저장이나 Kafka 행 변환은 수행하지 않으며, 하위 Spark 작업의 종료 코드를 `subprocess.run(..., check=True)`로 호출자에게 전달한다.

## 클래스와 메서드

### `Command.add_arguments(self, parser) -> None`

```text
--topic
  기본값 game.actions.v1.

--data-dir
  기본값 settings.DATA_DIR 문자열.

--progress-output
  선택 경로. 생략하면 data/marts/progress-game-actions.json을 사용.
```

### `Command.handle(self, *args, **options) -> None`

```text
options[data_dir]를 절대 Path로 변환
progress 출력 경로 결정
settings.SPARK_SUBMIT과 settings.SPARK_MASTER로 제출 명령 구성
executor core 1, total executor core 1 지정
settings.KAFKA_PACKAGE와 settings.DELTA_PACKAGE를 --packages로 연결
driver·executor Python을 현재 sys.executable로 지정
PROJECT_DIR/spark_jobs/game_actions_delta.py와 입력 인자 연결
PYSPARK_PYTHON과 PYSPARK_DRIVER_PYTHON 환경을 현재 Python으로 설정
subprocess.run(..., check=True) 호출
```

직접 호출: Django `settings`, Python `subprocess.run`, 외부 `spark-submit`.

## 주요 변수와 값 출처

- `data_dir`: `options["data_dir"]`의 절대 경로.
- `progress`: `--progress-output` 또는 `<data-dir>/marts/progress-game-actions.json`.
- `command`: Django 설정과 명령 옵션에서 조립한 `spark-submit` 인자 목록.
- `env`: 현재 프로세스 환경을 복사한 뒤 PySpark Python 경로를 추가한 환경 사전.

`total executor core`를 1로 제한하므로 계속 실행되는 Delta 스트림은 한 Worker만 점유한다. `without-nifi` 프로필의 두 번째 Worker는 일회성 집계 같은 별도 Spark 작업이 사용할 수 있다.
