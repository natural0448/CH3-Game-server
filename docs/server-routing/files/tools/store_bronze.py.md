# `tools/store_bronze.py`

## 책임과 호출 경계

수집한 NDJSON 원본 bytes를 새 Bronze 실행 폴더의 `events.ndjson`에 그대로 저장하고, 같은 bytes의 SHA-256·길이·행 수·파티션별 관찰 offset 범위를 `manifest.json`으로 남긴다. Kafka·Django·Spark는 호출하지 않는다.

## 명령줄 입력

- `--input: str`: 필수 수집 NDJSON 경로. `Path.read_bytes()`로 읽는다.
- `--run-id: str`: 필수 실행 ID. 하이픈을 제외한 문자는 영숫자여야 한다. 이미 같은 실행 폴더가 있으면 `mkdir(exist_ok=False)`가 중단한다.

## 최상위 처리 의사코드

```text
인자를 파싱하고 run-id 문자를 검사
입력 파일을 bytes로 읽고 비어 있지 않은 줄을 JSON으로 해석
data/lake/bronze/game/<run-id> 새 폴더를 생성
원본 bytes를 events.ndjson으로 그대로 기록
각 행의 partition과 offset으로 관찰 최소·최대 범위 계산
원본 bytes의 SHA-256, bytes 길이, 행 수, 입력 파일명만, UTC 수집 시각과 범위를 manifest에 저장
manifest JSON을 출력
```

직접 호출하는 외부 코드: `argparse.ArgumentParser`, `Path.read_bytes/mkdir/write_bytes/write_text`, `json.loads/dumps`, `hashlib.sha256`, `datetime.now(timezone.utc)`.

## 변수와 값의 출처

- `raw`: `--input` 파일에서 읽은 원본 bytes.
- `rows`: `raw`의 비어 있지 않은 각 줄에서 해석한 바깥 JSON 객체 목록.
- `root`: `data/lake/bronze/game/<run-id>`; 이번 저장의 새 폴더.
- `payload`: `root/events.ndjson`; `raw`를 변경하지 않고 저장할 위치.
- `ranges`: `rows`의 partition별 관찰 offset 최솟값·최댓값.
- `manifest`: `schema_version=1`, `run_id`, `source_topic=game.actions.v1`, `source_file_name=Path(args.input).name`, `rows`, `bytes`, `sha256`, `captured_at`, `offset_ranges`, `data_file=events.ndjson`. 입력의 절대경로는 기록하지 않는다.

정의한 함수·클래스와 반환값은 없다.
