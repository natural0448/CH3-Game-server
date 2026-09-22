# `server/analytics/management/commands/run_game_windows.py`

## 책임과 호출 위치

Django CLI에서 시간 창 작업의 인자를 받고 기존 Spark standalone 클러스터에 `spark_jobs/game_windows.py`를 제출한다. 이 계층은 Kafka JSON 해석, watermark 계산, 창 집계 또는 Parquet 쓰기를 직접 수행하지 않는다.

사용자는 `server` 폴더에서 `python manage.py run_game_windows --kind tumbling`로 호출한다.

## 클래스와 메서드

### `Command.add_arguments(parser) -> None`

- `parser`: Django가 전달하는 명령행 parser.

```text
--kind: tumbling|sliding, 기본값 tumbling
--topic: 기본값 game.actions.v1
--data-dir: 기본값 settings.DATA_DIR
```

Spark 작업은 `tumbling`과 `sliding`을 같은 입력 계약으로 실행하고, kind별 출력·checkpoint·progress 경로를 사용한다.

### `Command.handle(*args, **options) -> None`

- `args`: 현재 사용하지 않는 Django 위치 인자.
- `options`: 등록된 kind·topic·data-dir과 Django 공통 옵션.

```text
SPARK_MASTER가 기존 standalone cluster 주소인지 확인
PROJECT_DIR/spark_jobs/game_windows.py 존재 확인
Spark 4.1.3 Kafka package, driver 768m·executor 768m와 executor·총 4 core 제출 인자 조립
Spark 배포판에 이미 있는 org.slf4j:slf4j-api는 package 재배포 대상에서 제외
현재 Python을 driver·worker Python으로 지정
settings의 Kafka 주소와 사용자가 선택한 작업 인자를 전달
BASE_DIR에서 subprocess.run(check=True) 실행
Ctrl+C 안내 또는 Spark 비정상 종료를 CommandError로 변환
```

직접 호출하는 외부 코드는 Django `settings`, `pathlib.Path`, `subprocess.run`이다.

## 주요 변수와 값 출처

- `script`: `settings.PROJECT_DIR / "spark_jobs" / "game_windows.py"`.
- `command`: `SPARK_SUBMIT`, `SPARK_MASTER`, driver·executor 각각 768m, executor·총 4 core, Spark Kafka package와 `org.slf4j:slf4j-api` 제외 규칙, 현재 Python과 명령 인자에서 조립한다.
- `env`: 현재 환경 복사본에 `PYSPARK_PYTHON`과 `PYSPARK_DRIVER_PYTHON`을 `sys.executable`로 설정한다.
- Kafka 주소: `settings.KAFKA_BOOTSTRAP_SERVERS`를 쉼표로 연결한다.
