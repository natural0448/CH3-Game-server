# `server/analytics/management/commands/summarize_game.py`

## 책임과 호출 위치

Django CLI에서 원본 게임 JSONL 집계 인자를 받아 기존 Spark standalone 클러스터에 `spark_jobs/game_batch.py`를 제출한다. 집계 계산은 수행하지 않는다.

## 클래스와 메서드

### `Command.add_arguments(parser) -> None`

```text
--source: raw만 허용, 기본값 raw
--data-dir: 기본값 settings.DATA_DIR
--cores: 1|2, 기본값 2
```

### `Command.handle(*args, **options) -> None`

```text
driver 1g·executor 1g·executor core 1·총 core 선택값으로 제출 배열 구성
현재 Python을 driver와 worker Python으로 지정
PROJECT_DIR/spark_jobs/game_batch.py에 data-dir과 source 전달
BASE_DIR에서 subprocess.run(check=True) 실행
```

직접 호출하는 외부 코드는 Django `settings`, `pathlib.Path`, `subprocess.run`이다.

## 주요 변수와 값 출처

- `command`: Spark settings, 고정 1g 메모리 상한과 명령 옵션에서 조립한다.
- `env`: 현재 환경 복사본에 `PYSPARK_PYTHON`과 `PYSPARK_DRIVER_PYTHON`을 설정한다.
