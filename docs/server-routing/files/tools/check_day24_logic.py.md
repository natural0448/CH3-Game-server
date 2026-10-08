# tools/check_day24_logic.py

사용자가 다운로드한 `C:/Users/이해나/Downloads/check_day24_logic.py`를 bytes 그대로 복사한 교안 검사기다. 원본 SHA-256은 `39640dbe2885bda44988fdfe8b2044d0f8f72c48376688e24222550c078d0e2a`이며 이번 작업은 검사 논리를 수정하지 않았다. 교안 원본 URL은 `https://praxolve.net/encore/mlops2026/chapters/chapter-3/days/day-24/lessons/encore.chapter3.cdc-snapshot-change-workshop/embed-content/assets/day24-code/check_day24_logic.py`다.

## 책임과 실행 경계

저장된 학생 함수를 import하고 격리 시험 자료로 검사한다. 자체 Django 설정과 SQLite `:memory:`만 사용하며 프로젝트 settings·환경 파일·계정 DB를 읽지 않는다. 2~8교시는 `ads.mongo`의 DB 진입점을 금지 함수로 바꾼 뒤 학생 모듈을 읽는다. 시험 파일은 TemporaryDirectory 아래에서 생성·정리하며 정답 코드를 학생 파일에 쓰지 않는다. 실제 MySQL·MongoDB 수집 성공이나 CDC 실행 증거를 대신하지 않는다.

CLI의 필수 `--project`는 앱 패키지를 포함한 폴더 Path, 필수 `--period`는 정수 1~8, 선택 `--output`은 검사 JSON 저장 경로다. 1교시는 `<project>/game/management/commands/export_player_snapshot.py`, 나머지는 `<project>/ads/snapshot_intake.py`와 해당 관리명령을 찾는다. 검사기가 있다고 후속 교시의 학생 구현이 생기는 것은 아니다.

## 값의 출처와 소유자

- `FIELDS`: 모듈 상수 set. `schema_version`, `source_kind`, `captured_at`, `id`, `room_id`, `coins`, `version`, `updated_at` 정확히 8개.
- `PUBLIC`: 모듈 상수 list. `id`, `room_id`, `coins`, `version`, `updated_at` 순서.
- `CAUGHT`: 모듈 상수 tuple. `ValueError`, `TypeError`, `KeyError`, `OSError`.
- `Checks.results`: 각 인스턴스가 소유한 list; 처음은 빈 목록, 항목은 이름·passed bool·실패 error 문자열.
- Player·계정 시험 자료, 고정 UTC 시각, 예상 사전은 검사기가 만든 fixture다. 사용자의 실제 Player 자료가 아니다.
- `before`, `after`: main이 계산한 학생 소스 경로 → SHA-256 사전. 학생 파일 보존 확인에 쓴다.
- `report`: main이 소유. `period`, `project`, `passed`, `failed`, `database`, `mongo`, `student_sources_unchanged`, `source_sha256`, `checks`를 출력한다.

## helper 시그니처·반환값·직접 호출

| 실제 시그니처 | 파라미터와 반환값 | 의사코드·직접 호출 |
|---|---|---|
| `row(player_id=1, **updates)` | Player ID 기본 1, 임의 fixture 수정 키. 타입 제한을 두지 않는다. 새 dict 반환 | 고정 정상 8필드 → dict.update(updates); 실패 입력도 구성 |
| `public(value)` | PUBLIC 키를 가진 dict; 기본값 없음. 새 공개 5필드 dict | value[field]로 PUBLIC만 추출; 없는 키는 KeyError |
| `write_rows(path, values)` | 쓰기 가능한 Path와 JSON 직렬화 가능한 iterable; 기본값 없음. 받은 path 반환 | json.dumps(sort_keys=True, ensure_ascii=False) + 줄바꿈 → Path.write_text(UTF-8) |
| `equal(actual, expected)` | 비교할 두 값; 기본값 없음. 일치 시 None | !=이면 기대/실제값을 담은 AssertionError |
| `rejected(call, exceptions=CAUGHT)` | 인수 없는 callable와 기대 예외 클래스 tuple. 반환 None | callable 실행 → 허용 예외면 반환 → 정상 수락 시 AssertionError; 다른 예외는 전파 |
| `command(module_name, **options)` | 관리명령의 dotted 모듈 문자열, call_command 옵션. 정상 JSON dict 반환 | importlib.import_module → Command 생성 → django call_command(stdout=StringIO) → json.loads |

## class Checks

검사 결과 수집 클래스이며 외부 기반 클래스·클래스 상수는 없다.

| 실제 메서드 | 파라미터와 반환값 | 의사코드·직접 호출 |
|---|---|---|
| `Checks.__init__(self)` | 인스턴스; 기본값 없음. None | self.results = [] |
| `Checks.run(self, name, call)` | 이름 문자열, 인수 없는 callable. None | callable 실행 → Exception을 실패 항목으로 수집 → 정상은 passed=True; list.append |
| `Checks.mutation(self, name, call)` | 잘못된 결과 예의 이름과 callable. None | rejected(call, (AssertionError,))를 내부 검사로 구성 → self.run에 오답 감지 이름으로 전달 |

## 교시별 시험 함수

모든 함수는 기본값이 없으며 반환값은 None이다. `checks`는 Checks 수집기, `root`는 이 실행만의 임시 폴더 Path다. 2~8교시의 `module`은 실제 저장한 `ads.snapshot_intake` 모듈이다. 각 함수는 checks.run/mutation, 위 helper와 학생 함수를 직접 호출한다. 아래는 시험 책임이며 학생 하위 구현의 내부 로직을 복제하지 않는다.

| 실제 시그니처 | 직접 호출·간결한 동작 |
|---|---|
| `test_one(checks, root)` | get_user_model, schema_editor, 실제 game.models.Player 및 export 명령. 빈 QuerySet → 0 bytes, 2명 fixture → ID 순서·8필드·코인/버전·aware 시각·단일 수집 시각·행 수·bytes 해시 확인. patch로 naive 시각을 넣어 기존 파일 보존·임시 파일 정리 확인 |
| `test_two(checks, module, root)` | module.inspect_snapshot 및 inspect_player_snapshot 명령. 정상/빈 입력 확인 → 중복·타입·시각·schema·비공개 필드 등 잘못된 입력 거절 확인 |
| `test_three(checks, module, root)` | module.readiness 및 write_cdc_readiness 명령. 입력 여부와 경로 존재 분리 → 존재해도 CDC 미관찰 값 유지 → 저장 오류 확인 |
| `test_four(checks, module, root)` | module.change_player 및 write_player_change_fixture 명령. r/u/d fixture 해석 → 입력 보존·잘못된 상태 거절 → 원문/summary 분리·같은 출력 경로 거절 확인 |
| `test_five(checks, module, root)` | module.build_snapshot_contract/inspect_snapshot 및 write_snapshot_contract 명령. 검증 결과와 계약 일치 → 공개 필드·artifact·collector·시각 확인 → 잘못된 입력/원본 덮기 거절 |
| `test_six(checks, module, root)` | module.compare/load_rows 및 compare_player_snapshots 명령. 변경/신규/누락 구분 → 수집 시각만 다른 입력과 동등한 offset 확인 → 중복·naive·원본 덮기 거절 |
| `test_seven(checks, module, root)` | module.missing_summary 및 read_snapshot_missing 명령. 누락 ID 정렬·삭제 추론 금지 → 실제 결과 파일·실패 입력·원본 덮기 거절 확인 |
| `test_eight(checks, module, root)` | module.handoff_snapshot/build_snapshot_contract 및 handoff_player_snapshot 명령. 계약과 원본이 새 대상에서 일치 → 원본 보존·오류 경계·기존 대상 보존 확인 |

## main()

인수 없음. argparse가 sys.argv에서 위 CLI 인수를 읽는다. bool 반환: 실패가 하나라도 있으면 True(프로세스 종료 1), 전부 통과하면 False(종료 0). --help는 argparse의 정상 종료 0이다.

의사코드: `인수 파싱 → --project를 sys.path에 추가 → 이 프로세스 DJANGO_SETTINGS_MODULE 제거 → Django(SQLite 메모리) 직접 설정/setup → 학생 소스 해시 → 선택 교시 시험을 임시 폴더에서 실행 → 예외를 실패로 수집 → 소스 해시 재확인 → JSON 출력/선택 저장 → 실패 여부 반환`.

직접 호출: argparse, Path, hashlib, sys/os의 프로세스 설정, django settings.configure/setup, importlib, tempfile.TemporaryDirectory, 각 test 함수, Checks, json.dumps, Path.write_text, print. 직접 설정용 시험 문자열은 실제 환경 비밀값이 아니다. 학생 파일은 해시 확인만 하고 --output 검사 보고서와 시험 파일만 쓴다.

## 이 폴더 구조에서 실행

게임 저장소 루트에서 `server/.venv/Scripts/python.exe -X utf8 -B tools/check_day24_logic.py --project server --period 1`로 실행한다. manage.py와 game 앱은 server/ 아래에 있으며 현재 snapshot 명령은 해당 game 앱에 있다. 임시 시험 자료는 검사 프로세스에서만 사용하고 실제 DB에 넣지 않는다. 실제 export는 저장소 루트에서 `python server/manage.py export_player_snapshot --output data/exports/player-cdc.ndjson`으로 실행해 기존 루트 data 폴더를 사용한다.
