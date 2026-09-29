# 19일차 3교시 Bronze 저장 인수인계

## 요청 목적과 완료 결과

- 교안 3교시의 작은 bytes 연습에 `rows` 출력을 추가했다.
- Bronze manifest에 입력 경로 대신 파일명만 담는 `source_file_name`을 추가했다.
- 비어 있던 `data/lake/bronze/game/capture-001` 디렉터리만 제거한 뒤 기존 수집 파일로 `capture-001`을 생성했다. `events.ndjson`과 `manifest.json`이 있다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`; 직전 커밋 `2b1dc91 day18 - finish`.
- staged·unstaged 변경 없음. 기존 untracked: `tools/basics/`, `tools/capture_game.py`, `tools/lake_inventory.py`, `tools/store_bronze.py`.
- 두 수정 대상 Python 파일은 작업 시작 전에 존재한 사용자 변경으로 취급하고, 수정 전 구현을 각각의 라우팅 문서에 먼저 기록했다.

## 이번 작업에서 변경한 파일과 책임 경계

- 수정: `tools/basics/day19_period03.py` — 고정 bytes의 줄 수 출력.
- 수정: `tools/store_bronze.py` — `Path(args.input).name`을 `source_file_name`에 기록. 원본 bytes, SHA-256, 기존 manifest 계약과 새 run-id 보호는 유지.
- 추가: `docs/server-routing/files/tools/basics/day19_period03.py.md`, `docs/server-routing/files/tools/store_bronze.py.md`, 이 문서.
- 수정: `docs/server-routing/README.md` — 두 개발 파일의 1:1 색인.
- 데이터 결과: `data/lake/bronze/game/capture-001/events.ndjson` 및 `manifest.json`. 코드가 읽은 입력은 기존 `data/exports/game-kafka.ndjson`이다.
- 다른 untracked 사용자 파일과 서버·Kafka·Spark 설정은 변경하지 않았다.

## 검증

- 두 Python 파일의 `py_compile` 통과.
- 작은 연습 출력: `bytes 18`, `same True`, `rows 1`.
- `store_bronze.py --input data/exports/game-kafka.ndjson --run-id capture-001` 성공: `rows=5763`, `bytes=4587767`, `source_file_name=game-kafka.ndjson`.
- 저장된 `events.ndjson`과 입력 파일의 bytes가 같고, manifest의 SHA-256·행 수·bytes 길이가 입력에 맞음을 확인했다.
- 라우팅 감사 도구에서 이번 두 파일은 문서·색인·파싱 누락이 없다. 전체 변경 범위 감사는 기존의 다른 untracked 파일 4개(`day19_period01.py`, `day19_period02.py`, `capture_game.py`, `lake_inventory.py`)에 대한 문서·색인 누락 8건으로 종료 코드 1이다. 요청 범위 밖이라 이 문서들은 수정하지 않았다.

## 남은 위험과 다음 순서

- `capture-001`은 이제 데이터가 있으므로 같은 `--run-id`로 다시 실행하면 의도대로 `FileExistsError`가 난다. 새 입력을 보존할 때는 새 run-id를 사용한다.
- 4교시 이후에는 `data/lake/bronze/game/capture-001/manifest.json`을 선택한 보존본의 설명서로 사용한다. 실제 파일이 같은지 bytes와 지문으로 확인한다.
