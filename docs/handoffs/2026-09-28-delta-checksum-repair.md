# Delta 로그 체크섬 복구 인수인계

## 요청 목적과 완료 결과

`python manage.py run_game_delta`가 기존 Delta 로그를 읽는 중 `ChecksumException`으로 끝나는 문제를 복구했다. 실제 Delta 커밋 JSON은 유효했지만, 커밋 8의 Hadoop 숨김 체크섬 보조 파일이 JSON 수정 전 내용의 체크섬을 보관하고 있었다. 원본과 보조 파일을 백업한 뒤 오래된 숨김 체크섬 파일 하나만 제거했다.

복구 후 스트리밍은 Kafka의 대기 데이터를 끝까지 읽어 Delta 커밋 9와 10을 생성했다. 마지막 처리 배치는 전달 행 2,605개에서 `event_id` 기준 고유 사실 2,602개를 반영했고, Kafka 최신 오프셋과 처리 오프셋이 같아졌다. 검증용 스트리밍은 `Ctrl+C`로 종료했으며 Spark master·worker와 Kafka broker는 사용자가 실행해 둔 상태를 유지했다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `ed45ba4 day17-finish`
- staged 변경: 없음
- 작업 시작 전에 존재한 수정 파일:
  - `server/game/urls.py`
  - `server/game/views.py`
  - `tools/measurement-notes.md`
- 작업 시작 전에 존재한 untracked 개발 파일:
  - `server/analytics/management/collect_game_metrics.py`
  - `server/game/management/commands/prepare_load_players.py`
  - `tools/compare_load.py`
  - `tools/read_load_result.py`
  - `tools/ws_load.py`
- 작업 시작 전에 존재한 라우팅·인수인계 문서는 사용자 개발 파일의 짝 문서를 포함하고 있었다. 기존 코드와 측정 기록은 수정하거나 되돌리지 않았다.

## 이번 작업에서 변경한 항목

데이터 복구:

- 백업 폴더 `data/backups/delta-log-checksum-20260928-v8/`에 커밋 8의 JSON·transaction checksum·Hadoop checksum 관련 파일을 보관했다.
- `data/lake/silver/game_actions/_delta_log/.00000000000000000008.json.crc`만 삭제했다.
- 실제 Delta 로그 `00000000000000000008.json`과 transaction checksum `00000000000000000008.crc`는 유지했다.
- 정상 실행으로 Delta 커밋 9·10과 version 10 checkpoint가 생성됐다.
- `data/checkpoints/game-actions-delta-v1/commits/9`가 생성됐고 `data/marts/progress-game-actions.json`이 최신 오프셋을 기록했다.
- `data/marts/game-summary.json`을 새 Delta snapshot 기준으로 다시 생성했다.

문서:

- `docs/server-routing/README.md`: 작업 시작 전에 발견한 사용자 개발 파일 두 개를 색인에 추가했다.
- `docs/server-routing/files/server/analytics/management/collect_game_metrics.py.md`: 현재 경로에서는 Django 관리명령으로 검색되지 않고 출력 구현도 끝나지 않은 실제 상태를 기록했다.
- `docs/server-routing/files/tools/compare_load.py.md`: 두 측정 JSON 비교 흐름과 입력값 출처를 기록했다.
- 이 인수인계 문서를 추가했다.

## 중요한 판단과 책임 경계

- 오류의 원인은 Delta JSON 손상이 아니라 JSON과 Hadoop 숨김 체크섬 보조 파일의 불일치였다. JSON 세 줄은 모두 개별 JSON object로 파싱됐다.
- Delta 로그 전체, checkpoint, Parquet 데이터는 지우지 않았다. 문제를 일으킨 커밋 8의 숨김 `.json.crc`만 재생성 가능 대상으로 처리했다.
- 첫 검증에서 Codex sandbox 계정은 Delta 로그 폴더에 쓰기 권한이 없어 커밋 단계가 거부됐다. 실제 사용자 권한으로 다시 실행해 정상 커밋을 확인했다. 이는 프로젝트 설정 오류가 아니다.
- `run_game_delta`는 계속 실행되는 streaming 명령이다. 검증에서는 Kafka lag가 0인 것을 확인한 뒤에만 종료했다.
- 사용자가 작성 중인 `collect_game_metrics.py`와 `compare_load.py`는 코드 수정 없이 현재 구현을 문서에만 반영했다.

## 라우팅 문서 정합화

작업 시작 시 새로 발견한 사용자 개발 파일 두 개에 대해 1:1 짝 문서를 추가하고 서버 라우팅 색인을 갱신했다. 시그니처, 파라미터, 직접 호출, 변수 출처와 아직 구현되지 않은 부분을 현재 코드 기준으로 적었다. 이번 복구는 실행 데이터의 체크섬 보조 파일을 다뤘으며 서버·Spark source code는 변경하지 않았다.

## 실행한 검사

```text
커밋 8 JSON의 각 줄을 JSON으로 파싱
결과: 3줄 모두 정상

python manage.py summarize_game --data-dir ../data --source delta --cores 2
결과: 성공, 복구 직후 기존 Delta version 8 읽기 확인

python manage.py run_game_delta
결과: Delta batch 10 완료, input 2,605 / unique 2,602, Kafka lag 0
검증 후 Ctrl+C로 종료

python manage.py summarize_game --data-dir ../data --source delta --cores 2
결과: 성공, Delta version 10 기준 event_count 5,707

python manage.py check
결과: System check identified no issues

python -m py_compile analytics/management/collect_game_metrics.py ../tools/compare_load.py
결과: 성공

git diff --check
결과: 오류 없음. 기존 파일의 LF/CRLF 경고만 출력
```

최종 `game-summary.json`은 `source=delta`, `record_count=5707`, `event_count=5707`이다. 행동별 합계와 방별 합계도 각각 5,707로 일치한다.

## 남은 위험과 후속 작업

- 커밋 8의 JSON을 다시 외부 편집기로 직접 수정하면 같은 체크섬 불일치가 재발할 수 있다. `_delta_log`는 Spark/Delta가 생성하도록 두어야 한다.
- `server/analytics/management/collect_game_metrics.py`는 `management/commands/` 경로가 아니고 결과 출력도 끝나지 않아 아직 `manage.py` 명령으로 실행할 수 없다. 이 파일은 별도 사용자 작업으로 남겨 두었다.
- `run_game_delta` 종료 시 보인 `KeyboardInterrupt`와 worker connection reset 경고는 검증 작업을 수동 종료하며 생긴 종료 로그다. 정상 처리된 커밋 10과는 무관하다.

## 다음 실행 순서

Spark master·worker와 Kafka broker가 실행 중인 상태에서 새 PowerShell을 열고 다음을 실행한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server\server
.\.venv\Scripts\python.exe manage.py run_game_delta
```

이 명령은 지속 실행한다. 종료할 때만 `Ctrl+C`를 누른다. 집계 snapshot이 필요할 때는 다른 PowerShell에서 다음을 실행한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server\server
.\.venv\Scripts\python.exe manage.py summarize_game --data-dir ..\data --source delta --cores 2
```
