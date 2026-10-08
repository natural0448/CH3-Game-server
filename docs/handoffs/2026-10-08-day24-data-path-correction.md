# 24일차 기존 data 폴더로 저장 경로 정정

## 요청과 결과

사용자가 server/ 밖 기존 data 폴더를 사용하도록 경로 정정을 요청했다. `config/settings.py`의 `DATA_DIR = PROJECT_DIR / "data"`와 실제 폴더를 확인했다. 이전에 에이전트가 server/에서 `--output data/...`를 안내한 것이 잘못된 저장 위치의 원인이었다.

사용자가 이미 생성한 `server/data/exports/player-cdc.ndjson`을 **`data/exports/player-cdc.ndjson`로 이동**했다. 13,275 bytes·56행이며 이동 전후 SHA-256은 `6ea30948a1c6924b186676511207bd2099683ca00cf1b1582cb595e6437375d0`로 동일하다. 실제 DB에서 다시 수집하거나 저장된 행을 수정하지 않았다. 기존 루트 exports의 game-kafka 파일 두 개도 hash가 보존됐다.

비어 있음을 확인한 `server/data/day24-check-temp`, `server/data/exports`, `server/data`만 비재귀 Remove-Item으로 제거했다. 삭제·이동 직전에 모든 절대 경로가 게임 저장소 안에 있음을 검사했고 대상 파일이 없을 때만 이동했다. 기존 파일을 덮어쓰지 않았다. 그 외 폴더와 파일은 보존했다.

## 작업 시작 Git 상태와 기존 사용자 변경

- Chapter3: **Git 상태 확인 불가: 저장소 아님**. 각 대상 저장소 경계는 별도 확인했다. 초기화하지 않았다.
- 게임 HEAD: `5fd757d day23 진행사항`. 기존 unstaged는 `docs/server-routing/README.md`, staged는 없음. 기존 untracked에는 이전 검토의 공식 checker·짝 문서·인수인계·증거와 `server/game/management/commands/export_player_snapshot.py`가 있었다.
- 광고 HEAD: `8f541e4 day23 - finish`. 기존 staged·unstaged 없음. 이전 검토의 checker·문서·증거가 untracked로 남아 있었다. 옛 `ads/management/commands/export_player_snapshot.py`는 이번 요청 전에 이미 없어졌다.
- 사용자가 게임 앱으로 옮기고 교안대로 수정한 Python 명령과 실제 snapshot은 **작업 시작 전에 존재한 변경**이다. 에이전트의 코드 구현으로 주장하지 않는다.
- 시작 상태의 전체 staged·unstaged·untracked 목록은 두 저장소 `docs/server-routing/verification/day24-data-path-correction/start-state.json`에 있다. 환경 파일은 hash만 기록했고 값·비밀값은 복사하지 않았다.

## 추가·수정·이동·삭제한 파일과 책임

- 데이터 이동: `server/data/exports/player-cdc.ndjson` → `data/exports/player-cdc.ndjson`. Git의 **/data/ 제외 규칙 때문에 Git diff만으로는 나타나지 않으며 artifact-move.json과 hash로 확인한다.
- 문서 이동·정합화: 광고의 옛 `files/ads/management/commands/export_player_snapshot.py.md`를 제거하고 게임의 `files/server/game/management/commands/export_player_snapshot.py.md`에 현재 실제 구현을 문서화했다. **데이터 이동 전에** 사용자 Python 코드의 문서 정합화를 먼저 수행했다.
- 색인 수정: 게임 `docs/server-routing/README.md`에 실제 명령 등록, 광고 `day24-period01-index.md`에서 사라진 광고 명령을 제거하고 게임 문서·루트 data 입력 경로 연결.
- 이동한 데이터 파일의 짝 문서: `docs/server-routing/files/data/exports/player-cdc.ndjson.md`. 현재 관찰 행 수·bytes·해시·공개 스키마·생산자/소비자 경로를 기록하고 게임 색인에 연결했다.
- `.gitignore` 최소 수정과 짝 문서 `files/.gitignore.md`: 기존 **/data/ 규칙이 데이터 짝 문서까지 숨겼으므로 이 문서 한 경로만 재포함했다. 실제 data 산출물·환경 제외 규칙은 보존하고 git check-ignore로 검증했다.
- 안내 수정: 게임 checker 짝 문서와 두 저장소의 최초 검토 인수인계. 과거 실패 결과·초기 Git 상태는 역사 기록으로 보존하고 현재 실행 명령을 정정했다.
- 추가 기록: 이 인수인계, 광고의 해당 범위 인수인계, 두 저장소 검증 증거 폴더.
- Python·settings·manage.py·공식 checker·환경 파일은 수정하지 않았다. 현재 명령은 교안대로 Path(options["output"])를 사용하며 실제 출력 경로는 실행 폴더와 인수가 정한다. DATA_DIR를 명령에 임의로 주입하지 않았다.

## 올바른 VS Code PowerShell 명령

기존 Game-server 저장소 루트에서 기존 server/.venv를 활성화한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\server\.venv\Scripts\Activate.ps1
python tools/check_day24_logic.py --project server --period 1
```

검사 `failed=0`을 확인한다. snapshot은 이미 올바른 위치에 있으므로 다시 내보낼 필요는 없다. 이후 다시 수집할 때는 기존 증거를 보존할 새 파일명을 사용한다. 아래는 최초 생성에 사용할 표준 경로다.

```powershell
python server/manage.py export_player_snapshot --output data/exports/player-cdc.ndjson
```

server/ 폴더에서 실행한다면 같은 위치를 가리키는 인수는 `--output ../data/exports/player-cdc.ndjson`이다. root의 DATA_DIR와 manage.py 위치를 혼동하지 않는다.

광고의 2교시 소비 입력은 광고 작업 폴더 기준 **`../Game-server/data/exports/player-cdc.ndjson`**, 절대 경로는 `C:/MLO01-01/Chapter3/Game-server/data/exports/player-cdc.ndjson`이다. 기존 광고 프로젝트·환경·DB와 파일 구조를 유지한다. snapshot_intake.py 및 이후 교시 구현은 이번 범위가 아니다. 서버 실행·종료는 사용자 VS Code 터미널에서 진행한다.

## 테스트 결과

| 검사 | 결과 |
|---|---|
| 현재 게임 명령 공식 1교시 checker | 종료 0, **passed=12 / failed=0**, 학생 소스 변경 없음 |
| `server/manage.py export_player_snapshot --help` | 종료 0, 현재 명령 로드·필수 --output 정상 |
| 이동된 실제 snapshot | 56행, 정확한 8필드, 올바른 schema/source, 공개 타입, ID 오름차순·고유, 단일 captured_at, aware 시각 통과 |
| 파일 무결성 | 이동 전후 bytes·SHA-256 동일. 기존 game-kafka 파일 보존 |
| 경로 | root data/exports 파일 존재, 잘못 생성된 server/data 없음 |

공식 검사는 실제 게임 프로젝트의 저장 명령을 격리 SQLite 메모리 DB에서 실행했다. sandbox 기본 TEMP 제한을 피하려고 이 프로세스에서만 TEMP/TMP를 기존 `data/practice`로 지정했다. 검사기·환경 파일을 수정하지 않았고 시험 폴더는 종료 시 정리됐다. 실제 MySQL·MongoDB 쓰기와 서버 실행/종료는 없었다.

기존 사용자가 생성한 파일의 현재 형식·해시는 직접 검사했으며 게임 전체 DB가 같은 시점의 snapshot이었는지나 binlog CDC 실행 여부까지 입증한 것은 아니다. 실제 DB를 다시 export하는 명령은 사용자에게 남겼다.

## 마감 문서 정합화·검증 근거

코드·데이터 검증 뒤 별도 단계에서 현재 명령/검사기의 1:1 짝 문서와 두 색인을 재확인했다. 게임 표준 routing-doc-auditor 결과는 `routing-final.json`, 광고는 기존 README 부재를 보존하며 같은 스킬 AST API와 별도 색인으로 검사한 `routing-final-scoped.json`을 따른다. 광고의 사라진 source에 짝 문서가 남지 않도록 확인했다.

검증 폴더 `docs/server-routing/verification/day24-data-path-correction/`에는 start-state.json, data-layout-before.json, pre-operation-doc-check.json, artifact-move.json, snapshot-check.json, period01-official-current.json, 라우팅 검사와 finish-state.json이 있다. 이번 snapshot 이동은 별도로 기록하고 사용자의 Python 수정·이동은 기존 변경으로 구분했다. Git stage·commit·reset을 수행하지 않았다.
