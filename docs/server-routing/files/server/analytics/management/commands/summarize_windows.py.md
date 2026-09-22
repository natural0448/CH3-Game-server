# `server/analytics/management/commands/summarize_windows.py`

## 책임

Django 설정에 등록된 기존 Spark 클러스터에 시간 창 스냅샷 작업을 제출한다. 집계 계산과 JSON 작성은 `spark_jobs/summarize_windows.py`에 맡긴다.

## 클래스

### `Command(BaseCommand)`

#### `add_arguments(self, parser) -> None`

- `--data-dir`: 데이터 루트. 기본값은 `settings.DATA_DIR`이다.
- `--rows`: 창 종류마다 게시할 행 수. `5`, `10`, `20` 중 하나이며 기본값은 `20`이다.

#### `handle(self, *args, **options) -> None`

의사코드:

```text
settings.SPARK_SUBMIT과 settings.SPARK_MASTER로 제출 명령을 만든다
현재 Django Python 실행 파일을 driver·executor Python으로 지정한다
spark_jobs/summarize_windows.py에 절대 data-dir과 rows를 전달한다
settings.BASE_DIR에서 하위 프로세스를 실행하고 완료를 기다린다
프로세스 시작 또는 실행 실패를 Django CommandError로 바꾼다
```

직접 호출하는 외부 코드는 `subprocess.run`과 `spark_jobs/summarize_windows.py`이다. 성공 결과는 해당 Spark 작업이 게시한 `marts/windows.json`이다.

## 변수·상수

- `help`: 관리 명령의 용도를 설명하는 Django 도움말 문자열.
- `command`: Spark master, core 수, Python 경로, 작업 경로와 사용자 인자로 구성한 실행 배열.
- `env`: 현재 프로세스 환경을 복사하고 `PYSPARK_PYTHON`, `PYSPARK_DRIVER_PYTHON`을 현재 Python으로 고정한 값.

