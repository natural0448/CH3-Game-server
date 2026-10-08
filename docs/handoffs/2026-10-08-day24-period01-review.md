# 24일차 진행 준비와 1교시 검토

> 후속 정정: 사용자가 게임 명령을 교안대로 수정했고 현재 공식 검사 12개 통과·0개 실패다. 기존 data 폴더는 `Game-server/data`이며 이전의 server 작업 폴더 기준 출력 안내는 잘못됐다. 아래 실행 명령·수신 경로는 정정했다. 처음 실패했던 검사와 최초 Git 상태는 과거 관찰로 보존하며, 최신 결과·파일 이동은 [저장 경로 정정 인수인계](2026-10-08-day24-data-path-correction.md)를 따른다.

## 최초 검토의 요청 목적·결과

사용자가 제공한 `C:/Users/이해나/Desktop/실제 Player snapshot을 광고 서버에서 검증하고 인계하기.html`의 실행 준비와 **1교시**를 현재 저장 파일에 대조했다. 검토와 공식 검사 도구 준비는 완료했다. **현재 학생 구현의 1교시 완료 판정은 실패**다. 진행 중인 사용자 코드를 수정·이동·삭제하거나 뒤 교시 정답을 미리 적용하지 않았다.

두 저장소의 `tools/check_day24_logic.py`는 사용자가 알려 준 Downloads의 공식 원본과 bytes 동일하다. SHA-256은 `39640dbe2885bda44988fdfe8b2044d0f8f72c48376688e24222550c078d0e2a`다. 초기 HTTP 다운로드는 로그인 HTML이었으므로 Python 파일로 설치하지 않았다.

## 작업 시작 전 Git 상태

| 경계 | HEAD | 기존 staged·unstaged | 기존 untracked |
|---|---|---|---|
| Game-server | `5fd757d day23 진행사항` | 없음 | 없음 |
| ad_server | `8f541e4 day23 - finish` | 없음 | `ads/management/commands/export_player_snapshot.py` |

`Chapter3`: **Git 상태 확인 불가: 저장소 아님**. 상위 `C:/MLO01-01`은 접근 권한으로 Git 확인 불가였다. 두 대상 저장소 경계는 별도로 확인했다. 저장소를 초기화하지 않았다. 하위 AGENTS.md는 없으며 Chapter3 지침을 적용했다.

시작 상태·환경 파일 hash는 각 저장소 `docs/server-routing/verification/day24-period01-review/start-state.json`에 있다. 환경 값과 비밀값은 기록하지 않았다. 광고 원본은 광고 검증 폴더의 `export_player_snapshot-start.txt`로 보관했다. 기존 사용자 파일의 짝 문서와 색인을 먼저 작성한 뒤 검사기를 추가했다.

## 최초 검토 당시 1교시 판정

| 확인 항목 | 실제 관찰 | 판정 |
|---|---|---|
| 실행 프로젝트·파일 위치 | 사용자 파일은 `ad_server/ads/management/commands/`에 있음. 게임 `server/game/management/commands/`에는 없음 | 불일치 |
| 실제 Player 조회 필드 | `name`, `level`, `score`는 모델에 없음 | 불일치 |
| 행 메타데이터 | `schema`, `source="players"`로 작성. 교안은 `schema_version`, `source_kind="player-snapshot"` | 불일치 |
| Command 정의·CLI | Command 한 개, 빈칸 없음, 필수 --output 정의는 교안과 일치 | 일치 |
| aware 시각·파일 교체 구조 | 수집 시각은 반복 밖 한 번, updated_at naive 거절, 임시 파일 후 os.replace | 제공부 구조 일치 |
| 게임 환경 | Python 3.12.13, 기존 MySQL, USE_TZ=True, 공개 다섯 필드 존재 | 준비 정상 |
| 실제 DB 연결 | 읽기 전용 `Player.objects.count()` 성공, Player 56명 | 연결 정상 |
| 실제 snapshot | 최초 검토 당시 파일 미생성. 올바른 대상은 `data/exports/player-cdc.ndjson` | 이후 사용자 생성본을 루트 data/exports로 이동; 최신 인수인계 참조 |

광고에서 실행하면 `ModuleNotFoundError: No module named 'game'`다. 게임에서 실행하면 `Unknown command: export_player_snapshot`다. 파일 위치만 바꾸더라도 잘못된 ORM 필드 때문에 `FieldError`가 발생하며, 조회 필드만 고쳐도 행 메타데이터 검사에 실패한다. stdout의 올바른 schema 선언은 잘못된 NDJSON 행을 보정하지 않는다.

## 최초 검토의 수정 안내 — 이후 사용자 적용

아래는 최초 검토에서 제안한 내용이다. 이후 사용자가 실제 게임 앱에 저장하고 공개 필드·메타데이터를 수정했다. 에이전트의 Python 변경으로 주장하지 않는다.

1. 기존 코드를 보관한 뒤 게임 파일 위치를 `C:/MLO01-01/Chapter3/Game-server/server/game/management/commands/export_player_snapshot.py`로 맞춘다. 이 프로젝트에는 management/commands와 각 `__init__.py`가 이미 있다. 광고의 INSTALLED_APPS나 import 경로에 game을 추가하지 않는다.
2. 문제 1의 조회는 실제 공개 다섯 필드로 작성한다.

```python
rows = Player.objects.order_by("id").values(
    "id", "room_id", "coins", "version", "updated_at").iterator()
```

3. 문제 2는 교안의 행 이름 `row`와 메타데이터를 사용한다. 문제 3의 json.dumps 대상도 `row`로 맞춘다. ORM iterator 이름 rows를 행 사전으로 재대입하지 않는다.

```python
row = {"schema_version": "player-snapshot/v1",
       "source_kind": "player-snapshot", "captured_at": captured_at,
       **player, "updated_at": updated_at.isoformat()}
stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
count += 1
```

4. 제공 import·시각 검사·임시 파일 정리·os.replace·stdout 반환부는 이어 쓴다. 먼저 공식 격리 검사를 통과시킨 뒤 실제 내보내기를 실행한다.

## 사용자가 VS Code에서 실행할 명령

게임 저장소 루트의 PowerShell 터미널에서 실행한다. 관리 명령 파일은 server/ 안에 있지만 기존 data 폴더는 저장소 루트에 있다. 기존 server/.venv를 사용하며 새 환경·프로젝트를 만들지 않는다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\server\.venv\Scripts\Activate.ps1
python tools/check_day24_logic.py --project server --period 1
```

검사 JSON의 `failed=0`과 항목별 passed를 확인한 뒤 실행한다.

```powershell
python server/manage.py export_player_snapshot --output data/exports/player-cdc.ndjson
```

반환 rows·captured_at·sha256을 기록한다. 현재 DB에는 Player 56명이 있었지만 게임 사용 중 추가·삭제될 수 있으므로 내보내기 행 수를 56으로 강제하지 않는다. NDJSON의 각 행이 정확히 8필드인지, ID 순서·동일 captured_at·aware updated_at·실제 bytes 해시를 확인한다. 이미 증거 파일을 만들었다면 재수집 전에 원본을 보존하고 새 출력 이름을 사용한다.

이 명령은 DB를 조회하는 파일 내보내기이며 Django runserver가 필요하지 않다. MySQL 연결은 필요하다. 1교시에는 MongoDB·Kafka·Connect·Debezium을 새로 실행할 이유가 없다. 모든 서버 실행·종료는 사용자가 기존 VS Code 터미널에서 담당한다.

**2교시 준비:** 광고는 게임 ORM을 import하지 않고 파일을 받는다. 광고 작업 폴더에서 사용할 입력 경로는 `../Game-server/data/exports/player-cdc.ndjson`이다. 실제 절대 경로는 `C:/MLO01-01/Chapter3/Game-server/data/exports/player-cdc.ndjson`이다. 후속 정정에서 사용자가 생성한 실제 입력을 이 위치로 옮겼다. `ads/snapshot_intake.py`는 아직 없으며 구현하지 않았다. 교안의 `../game_server/`를 현재 폴더 이름으로 바꾸는 것 외에 계약을 임의 변경하지 않는다. 광고의 `ads.exporting.read_ndjson`·`ads.timestamps.parse_utc`가 기존에 존재함을 확인했다.

## 최초 검토의 변경 파일·설계 경계

게임 저장소의 새 개발 파일은 **`tools/check_day24_logic.py` 하나**다. README의 해당 검사기 항목 추가, 짝 문서 `docs/server-routing/files/tools/check_day24_logic.py.md`, 이 인수인계와 검토 증거를 추가했다. 게임 앱·모델·manage.py·settings·환경 파일은 수정하지 않았다.

광고 저장소는 공식 검사기와 그 짝 문서, 기존 사용자 명령의 짝 문서, 별도 색인, 인수인계·검토 증거만 추가했다. 기존 사용자 `export_player_snapshot.py`는 이번 작업의 코드 추가로 주장하지 않는다. 광고의 기존 README 부재를 되돌리지 않았다.

## 최초 검토의 테스트·검사 결과

| 실행·확인 | 결과 |
|---|---|
| 게임 `server/.venv/Scripts/python.exe -X utf8 -B server/manage.py check` | 종료 0, Django 문제 없음 |
| 광고 `.venv/Scripts/python.exe -X utf8 -B ad_config/manage.py check` | 종료 0, Django 문제 없음 |
| 광고 원본 명령 --help | 종료 1, game import 실패 재현 |
| 게임 명령 --help | 종료 1, 명령 미등록 재현 |
| 공식 검사기 --help | 종료 0, CLI 준비 정상 |
| 공식 1교시 검사 `--project server` | 종료 1, passed=1/failed=1. 원본 파일 보존만 통과, 게임 명령 로드 실패 |
| 사용자 코드 원문을 임시 게임 폴더에 복사해 공식 검사 | 종료 1, passed=1/failed=3. 잘못된 name 필드와 후속 파일 부재 확인 |
| 조회 필드만 바꾼 진단용 임시 사본 검사 | 종료 1, passed=11/failed=1. 정확한 8필드 검사 실패; schema/source가 원인 |
| 실제 게임 DB 읽기 전용 점검 | 성공. 공개 필드 존재·Player count=56. 기존 DB 쓰기 없음 |
| 교안 AST 대조 | Command 한 개, 빈칸 없음, add_arguments 일치, handle 불일치 |

임시 사본 결과는 **현재 사용자 코드의 통과 결과가 아니다**. 원본 source hash는 보존됐으며 임시 프로젝트는 검사 후 정리했다. 정답을 원본에 주입하지 않았다. 초기 sandbox TEMP 접근 실패는 학생 코드 실패로 취급하지 않았고, 이 검사 프로세스에서만 TEMP/TMP를 작업 공간 안의 새 `server/data/day24-check-temp/`로 지정해 다시 실행했다. 원본 검사기·환경 파일을 수정하지 않았다. 빈 시험 부모 폴더가 남아 있지만 원본·fixture 파일은 없다.

검증 근거는 `docs/server-routing/verification/day24-period01-review/`의 `period01-current-project.json`, `period01-isolated-as-written.json`, `period01-isolated-query-fields-only-diagnostic.json`, `isolated-review-summary.json`, `runtime-readiness.json`, `checker-origin-local.json` 및 광고의 `lesson-comparison.json`이다.

## 최초 검토의 문서 정합화와 후속 정정

검증 후 별도 단계에서 이번 검사기·광고 사용자 명령의 짝 문서와 색인을 재확인했다. 게임 표준 라우팅 검사와 광고의 같은 스킬 AST API 검사를 실행했다. 최종 결과는 게임 `routing-final.json`, 광고 `routing-final-scoped.json`에 기록한다. 광고 표준 CLI는 기존 README 부재 때문에 사용할 수 없으며 그 제한은 `routing-before.json`에 남겼다.

최초 검토에서는 실제 export를 사용자에게 맡겼다. 이후 사용자가 코드를 수정하고 공개 파일을 생성했다. 경로 정정 작업에서 공식 격리 검사 12개가 모두 통과했고 실제 56행 파일 형식·해시를 확인했다. 최신 문서와 이동 결과는 저장 경로 정정 인수인계를 따른다. 계약·소비 검증·인계는 각 후속 교시에서 진행한다. 일반 파일 snapshot과 MySQL binlog CDC를 같은 것으로 기록하지 않는다.

작업 종료 Git 상태·기존 사용자 원본 보존·환경 hash·검사기 bytes 일치는 각 저장소 `finish-state.json`에서 확인한다. staged 변경은 만들지 않았다. 기존 사용자 코드와 이번 검사 도구 추가를 구분해서 기록했다.
