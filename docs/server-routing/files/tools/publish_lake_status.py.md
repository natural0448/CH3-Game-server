# tools/publish_lake_status.py

## 책임과 호출 경계

교안의 원본 보존 검사 결과 게시 도구다. 선택한 원본·로컬 사본을 같은 원본 manifest의 bytes·rows·sha256과 비교하고 `data/marts/lake-status.json`에 마지막 결과를 게시한다. 파일 복사, Kafka 소비, Spark 실행, 게임 state 변경은 하지 않는다. Django API는 별도로 게시 파일을 읽는다.

## 함수 시그니처·입력·반환·의사코드

### `inspect_file(path)`

- path: 읽을 파일의 문자열 또는 Path, 필수. 기본값 없음.
- 반환: bytes(파일 길이), rows(빈 줄 제외 행 수), sha256(16진 지문) 사전.

```text
raw <- Path(path).read_bytes()
bytes <- len(raw)
rows <- raw.splitlines() 중 strip()이 비어 있지 않은 행 수
sha256 <- hashlib.sha256(raw).hexdigest()
세 값 반환
```

### `compare_to_manifest(observed, manifest)`

- observed: inspect_file의 사전. manifest: 원본 설명서 사전. 두 값 모두 필수이며 bytes·rows·sha256 키가 있어야 한다.
- 반환: 세 키에 대한 bool 비교 사전.

```text
각 key in (bytes, rows, sha256)에 observed[key] == manifest[key] 기록
비교 사전 반환
```

외부 코드 호출 없음. 필수 키 누락은 KeyError로 드러난다.

### `make_status(original_path, copied_path, manifest_path)`

- 세 필수 입력: 원본 NDJSON, 같은 수집본의 사본 NDJSON, 원본 manifest JSON 경로. 문자열 또는 Path, 기본값 없음.
- 반환: schema_version=1인 검사 결과 사전. 숫자는 원본 실제 bytes에서 얻는다.

```text
manifest <- json.loads(Path(manifest_path).read_text(encoding="utf-8"))
original, copied <- 각각 inspect_file 호출
original_checks, copied_checks <- 각각 compare_to_manifest 호출
manifest의 run_id/source_topic/captured_at과 실제 원본 rows/bytes/sha256 결합
generated_at <- datetime.now(timezone.utc).isoformat()
matched <- 원본 비교 세 개와 사본 비교 세 개가 모두 True
verification_scope <- "local-and-copied-bytes"
검사 결과 반환
```

### `write_status(status, output)`

- status: make_status 반환 사전. output: 게시 파일의 문자열 또는 Path. 모두 필수.
- 반환: None.

```text
target <- Path(output)
target.parent.mkdir(parents=True, exist_ok=True)
temporary <- target.with_suffix(target.suffix + ".tmp")
json.dumps(status, ensure_ascii=False, indent=2)를 UTF-8로 temporary에 쓰기
temporary.replace(target)로 마지막 게시 파일 교체
```

기존 게시 파일은 새 검사가 끝난 뒤 교체된다. 원본·사본은 쓰지 않는다. 동시 게시 실행은 지원하지 않는다.

### `main()`

- 파라미터 없음. 반환 None. CLI 인자는 argparse가 받는다.
- `--original`, `--copied`, `--manifest`: 필수 파일 경로.
- `--output`: 기본값 `data/marts/lake-status.json`. 상대경로는 실행 위치 기준이다.

```text
argparse.ArgumentParser로 인자 읽기
make_status로 검사
write_status로 게시
print(json.dumps(status, ensure_ascii=False, indent=2))
matched=False이면 SystemExit로 실패 종료 (실패 검사 결과도 게시됨)
```

파일 없음·잘못된 manifest는 예외로 종료하며 새 상태를 게시하지 않는다. 실행 진입점은 `__name__ == "__main__"`이다.

## 변수·값 출처

- `raw`, `original`, `copied`: 선택한 파일의 실제 bytes와 inspect_file 결과.
- `manifest`: 사용자가 지정한 원본 설명서. run_id, source_topic, captured_at, bytes, rows, sha256의 출처.
- `original_checks`, `copied_checks`: manifest와의 bool 비교 결과, make_status만 작성한다.
- `schema_version=1`, `dataset_id="village.game-actions"`, `verification_scope="local-and-copied-bytes"`: 도구의 고정 게시 계약.
- `generated_at`: 검사 시점 UTC. 원본 captured_at을 대체하지 않는다.
- `target`, `temporary`: CLI output과 동일 폴더의 `.tmp` 경로. write_status만 작성한다.
- `parser`, `args`, `status`: main 소유의 인자 정의·해석 결과·이번 검사 사전.

## 실행

Game-server 루트에서 실행한다. 현재 선택한 수집본은 capture-001이다.

```powershell
.\server\.venv\Scripts\python.exe tools/publish_lake_status.py --original data/lake/bronze/game/capture-001/events.ndjson --copied data/copies/bronze/game/capture-001/events.ndjson --manifest data/lake/bronze/game/capture-001/manifest.json
```

클라이언트의 새로고침은 이 명령을 실행하지 않고 기존 `/api/analytics/lake/` GET만 수행한다.
