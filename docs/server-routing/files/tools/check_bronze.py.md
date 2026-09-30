# tools/check_bronze.py

## 책임과 호출 계층

로컬 사본 bytes를 같은 수집본의 원본 manifest와 비교한다. 복사 무결성만 검사하며 이벤트의 의미·타입을 검증하거나 다른 서비스를 호출하지 않는다.

## 입력·변수·출력

- `p`: ArgumentParser. 필수 문자열 `--data`는 검사할 NDJSON 사본 경로, `--manifest`는 원본 manifest JSON 경로다.
- `args`: parse_args 결과.
- `raw`: `Path(args.data).read_bytes()`의 bytes.
- `manifest`: UTF-8으로 읽어 json.loads한 원본 설명서. `run_id/bytes/sha256/rows` 필드가 필요하다.
- `observed`: 실제 bytes 길이, SHA-256 hex 문자열, 공백뿐인 줄을 제외한 행 수.
- `checks`: observed의 각 키를 manifest와 비교한 bool 사전. 키는 `bytes`, `sha256`, `rows`다.
- 콘솔 JSON 최상위: `run_id=manifest["run_id"]`, `observed`, `checks`. JSON은 성공·불일치 모두 한 번만 출력한다.

## 실행 의사코드

```text
CLI 인자를 읽는다
Path로 사본 bytes와 manifest JSON을 읽는다
len, hashlib.sha256, splitlines로 실제 값을 계산한다
manifest와 각 값을 비교한다
json.dumps로 run_id/observed/checks를 한 번 출력한다
all(checks.values())가 False이면 SystemExit("copy does not match manifest")
```

직접 외부 호출: argparse, pathlib 읽기, json.loads/dumps, hashlib.sha256. 정상 종료 코드는 0, 불일치는 0이 아닌 코드다. 정의한 함수·클래스·메서드 및 반환값은 없다. 검사 중 원본·사본을 쓰지 않는다.
