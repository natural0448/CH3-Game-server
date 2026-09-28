# `server/game/management/commands/prepare_load_players.py`

## 책임과 호출 경계

Django 인증 사용자와 `Player`를 20명 단위 방에 준비하고, 비밀번호를 제외한 계정 목록 JSON을 저장한다. 기존 사용자 비밀번호와 기존 Player 상태를 덮어쓰지 않는다.

## 클래스와 메서드

### `Command.add_arguments(self, parser) -> None`

파라미터:

- `parser`: Django 관리 명령 argument parser.

```text
--count 정수, 기본 20 등록
--prefix 문자열, 기본 day18_ 등록
--rooms 문자열, 기본 load18 등록
--output 필수 경로 등록
```

직접 호출: argument parser의 `add_argument`.

### `Command.handle(self, *args, **options) -> None`

파라미터:

- `options["count"]`: 만들거나 확인할 누적 계정 수, 허용 범위 1..200.
- `options["prefix"]`: 사용자 이름 접두사.
- `options["rooms"]`: 방 이름 접두사.
- `options["output"]`: 계정 목록 JSON 출력 경로.

```text
입력 범위와 빈 접두사를 검사
getpass로 공통 비밀번호를 입력
transaction 안에서 번호별 User를 get_or_create
새 User만 set_password로 비밀번호 저장
기존 User의 비밀번호가 다르면 전체 실행 중단
20명 단위 room_id를 계산
Player가 없으면 방 정원 확인 후 초기 상태로 생성
기존 Player가 다른 방이면 전체 실행 중단
username, room_id, player_id만 rows에 수집
DB transaction 종료 후 임시 JSON을 만들고 output으로 교체
계정 수와 새 사용자 수를 표준 출력
```

직접 호출:

- `get_user_model`, `User.objects.get_or_create`, `check_password`, `set_password`.
- `Player.objects.filter`, `Player.objects.create`.
- `transaction.atomic`.
- `Path.write_text`, `Path.replace`, `json.dumps`.

## 변수와 값의 출처

- `username`: `prefix`와 1부터 시작하는 세 자리 번호.
- `room_id`: `rooms`와 20명 단위 방 번호.
- `password`: 터미널 `getpass` 입력이며 파일이나 로그에 저장하지 않는다.
- `rows`: 비밀번호 없는 계정 목록.
- `output`: 현재 작업 디렉터리를 기준으로 `--output`을 `resolve()`한 경로.
