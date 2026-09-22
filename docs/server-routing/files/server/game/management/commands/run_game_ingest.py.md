# `server/game/management/commands/run_game_ingest.py`

## 책임과 호출 위치

Django CLI의 수집 옵션을 기존 Spark standalone 클러스터의 `spark_jobs/game_ingest.py`에 전달한다. Kafka 해석, Parquet 쓰기와 checkpoint 관리는 Spark 작업 파일이 수행한다.

## 클래스와 메서드

### `Command.add_arguments(parser) -> None`

```text
--data-dir: 기본값 settings.DATA_DIR
--mode: continuous|available-now, 기본값 continuous
--cores: 1|2, 기본값 2
--max-offsets: 기본값 1000
--trigger-seconds: 기본값 5
```

### `Command.handle(*args, **options) -> None`

```text
standalone SPARK_MASTER와 양수 rate·interval 확인
PROJECT_DIR/spark_jobs/game_ingest.py 존재 확인
driver 1g·executor 1g·executor core 1·총 core 선택값으로 제출 배열 구성
Spark 4.1.3 Kafka package와 현재 Python 경로 지정
settings의 Kafka 주소와 고정 game.actions.v1 Topic 전달
subprocess.run(check=True) 실행
Ctrl+C는 output·checkpoint 보존 안내, 실패는 CommandError
```

직접 호출하는 외부 코드는 Django `settings`, `pathlib.Path`, `subprocess.run`이다.

## 주요 변수와 값 출처

- `script`: `settings.PROJECT_DIR / "spark_jobs" / "game_ingest.py"`.
- `command`: settings, 명령 옵션과 고정 1g 메모리 상한에서 조립한다.
- `env`: 현재 환경에 driver·worker Python으로 `sys.executable`을 지정한다.
