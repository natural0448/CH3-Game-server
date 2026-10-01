# infra/run-game-layers.sh

## 책임과 입력·변수

Windows PowerShell에서 한 줄씩 실행할 20일차 명령 보관. 사용자 요청으로 파일명 `.sh`는 유지하지만 Bash 실행 파일이 아니다. 사용자가 필요한 줄을 선택·복사해 PowerShell에서 실행한다. 함수·클래스·자동 실행기나 실패 감지 로직은 추가하지 않았다.

- 작업 디렉터리: `C:\MLO01-01\Chapter3\Game-server`를 `cd`로 지정한다.
- `python`: 사용자가 활성화한 가상환경의 실행 명령. 수집·보존·복사 도구에 사용한다.
- Spark 실행 파일: `C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd`. 각 명령에 실제 경로와 PowerShell 호출 연산자 `&`를 적는다.
- Master: 모든 Spark 호출의 `--master`는 `spark://127.0.0.1:7077`. 서비스는 별도로 준비되어 있어야 한다.
- 수집 ID: `capture-002`. 원본·사본이 이미 있으면 첫 수집·보존·복사 세 줄을 건너뛴다. 기존 run 보호 규칙은 각 도구가 담당한다.
- 파싱 입력: `data/copies/bronze/game/capture-002/events.ndjson`. 앞선 `copy_bronze.py`의 출력이다.
- 파싱·품질 출력: `data/lake/staging/parsed-capture-002`, `data/lake/staging/quality-capture-002`. 중복 제거 입력은 품질 출력의 `accepted` 하위 경로다.
- Silver 출력: `data/lake/silver/game_actions/capture-002-base`, `data/lake/silver/game_actions/capture-002`.
- Gold 출력: `data/lake/gold/game_daily/capture-002`. 채집 전용 출력은 `capture-002-gathered`로 분리한다.
- 화면 집계 출력: `data/marts/game-summary.json`.
- 계약 작성기만 사용하는 `$env:QUALITY_URI`, `$env:SILVER_URI`, `$env:GOLD_URI`는 위 경로의 `file:///C:/MLO01-01/Chapter3/Game-server/…` 절대 URI로 현재 PowerShell 세션에 설정한다. 앞선 Spark 호출은 이 변수를 참조하지 않는다. profile 파일에 의존하지 않는다.

## 직접 호출·의사코드

사용자 정의 시그니처·파라미터·반환값은 없다. CLI 인자는 명령에 적힌 고정값이며 외부 도구가 처리한다. 결과는 수집 파일·사본·Parquet·JSON과 콘솔 출력이다. 세 환경변수의 쓰기 소유자는 이 명령을 실행한 PowerShell 세션이다.

```text
cd(project root)
capture_game(--output data/exports/game-kafka-next.ndjson)
store_bronze(--input collected file, --run-id capture-002)
copy_bronze(--run-id capture-002) → copied events.ndjson와 manifest.json
spark-submit(parse_game_bronze, copied events → parsed-capture-002)
spark-submit(check_game_quality, parsed → quality-capture-002)
spark-submit(dedup_game_actions, quality/accepted → capture-002-base)
spark-submit(add_game_date, base → Silver capture-002)
spark-submit(build_game_daily, Silver → Gold capture-002)
spark-submit(publish_game_summary, Silver → data/marts/game-summary.json)
현재 세션의 QUALITY_URI/SILVER_URI/GOLD_URI 설정
spark-submit(write_layer_contract) → data/contracts/layer-contract.json
spark-submit(build_game_daily, --event-type player.gathered) → 별도 gathered Gold
사용자가 한 줄씩 실행하며, 앞 단계 실패 시 다음 줄을 실행하지 않는다
```

직접 호출은 `cd`, `python`과 위 외부 스크립트, Native `spark-submit.cmd`다. 호출 대상의 Python/Spark 내부 구현은 각 파일의 짝 문서에서 설명한다. 이 파일은 서비스를 시작·종료하거나 폴더를 삭제하지 않는다. 기존 Parquet 출력은 보호될 수 있으므로 사용자가 기존 결과를 재사용하거나 새 경로를 지정한다. summary와 계약 JSON은 해당 게시 도구의 기존 갱신 규칙을 따른다.
