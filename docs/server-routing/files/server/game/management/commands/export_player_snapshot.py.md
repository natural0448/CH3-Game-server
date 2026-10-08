# server/game/management/commands/export_player_snapshot.py

이 요청 시작 전에 사용자가 게임 앱으로 옮기고 교안대로 수정한 untracked 코드다. 이번 경로 정정 작업은 Python 내용을 수정하지 않았다. 이 짝 문서는 추가 파일 작업 전에 현재 구현에 맞췄다.

## 책임과 저장 경계

기존 `game.models.Player`의 공개 다섯 필드를 ID 순서로 읽고 `player-snapshot/v1` NDJSON을 만든다. DB를 변경하지 않는다. 광고 선택·노출·클릭 사건이나 binlog CDC를 만들지 않는다.

`target = Path(options["output"])`이므로 상대 출력 경로는 **프로세스 실행 폴더** 기준이다. `settings.BASE_DIR`나 `settings.DATA_DIR`를 자동으로 붙이지 않는다. 기존 `config/settings.py`의 `DATA_DIR = PROJECT_DIR / "data"`와 맞추려면 `C:/MLO01-01/Chapter3/Game-server`에서 `python server/manage.py export_player_snapshot --output data/exports/player-cdc.ndjson`으로 실행한다. 결과는 `C:/MLO01-01/Chapter3/Game-server/data/exports/player-cdc.ndjson`이다. server/에서 실행할 경우 출력 인수는 `../data/exports/player-cdc.ndjson`이다.

## class Command(BaseCommand)

Django 관리명령 기반 클래스. 클래스 소유 `help`는 `게임 공개 상태를 player-snapshot/v1 NDJSON으로 내보냅니다.`다. Django가 인스턴스를 생성해 호출한다.

## Command.add_arguments(self, parser)

`self`는 명령 인스턴스, `parser`는 Django의 argparse parser이며 기본값은 없다. `parser.add_argument("--output", required=True)`로 필수 경로 문자열을 받는다. 확장자 제한은 없다. 반환값은 `None`이다.

## Command.handle(self, *args, **options)

`self`는 명령 인스턴스다. 추가 위치 인수 `args`는 사용하지 않는다. 필수 `options["output"]`은 출력 파일 경로 문자열이다. 같은 경로의 기존 파일은 완성본으로 교체할 수 있으므로 증거 재수집은 새 파일명을 사용한다.

정상 반환은 `None`이며 stdout에 `path`, `rows`, `sha256`, `schema_version`, `source_kind`, `captured_at` JSON을 쓴다. 빈 QuerySet은 0바이트 파일·rows=0·captured_at=null을 반환한다. try 내부 `OSError`, `TypeError`, `ValueError`, `DatabaseError`는 임시 파일 정리 후 `CommandError`로 감싼다. 부모 폴더 생성 및 QuerySet 구성은 try 앞에 있으므로 그 위치의 오류는 원래 예외로 전파한다.

```text
출력 Path와 부모 폴더 준비 → captured_at을 한 번 생성
Player.objects를 id 순서로 공개 다섯 필드만 iterator 조회
같은 폴더의 임시 UTF-8 파일에 각 행 처리
updated_at이 naive이면 거절
공개 상태에 schema_version/source_kind/captured_at을 합침
updated_at을 ISO 문자열로 바꾸고 JSON 한 줄 작성 → count 증가
완성한 임시 파일 bytes SHA-256 → os.replace로 최종 경로 교체
실패 시 임시 파일 정리 → 정상 결과 JSON stdout
```

직접 호출: `Player.objects.order_by().values().iterator()`에서 공개 dict, `timezone.now/is_naive`, `Path.mkdir/read_bytes/unlink`, `tempfile.NamedTemporaryFile`, `json.dumps`, `hashlib.sha256`, `os.replace`, `self.stdout.write`. 하위 DB·Player 계정 내부 구현을 복제하지 않는다. 소스에서 게임 계정·비밀번호·세션·좌표 x/y를 조회하거나 쓰지 않는다.

## 값의 출처와 소유자

| 이름 | 실제 값 또는 출처 |
|---|---|
| `target` | `Path(options["output"])`; 실행 폴더 기준의 상대/절대 경로 |
| `captured_at` | 반복문 밖 `timezone.now().isoformat()`; 전체 행에 동일 값 |
| `rows` | 공개 id/room_id/coins/version/updated_at iterator |
| `player` | 조회한 현재 공개 dict |
| `updated_at` | Player datetime; aware 시각만 허용 |
| `row` | 정확히 8필드 dict; schema_version=`player-snapshot/v1`, source_kind=`player-snapshot`, updated_at은 ISO 문자열 |
| `temporary_path` | 초기 None, 파일을 연 뒤 실제 임시 Path |
| `count` | 초기 0, 실제 작성 한 행마다 +1 |
| `checksum` | 완성한 임시 파일 bytes의 SHA-256 hex 문자열 |

지역 변수는 해당 handle 호출이 소유한다. 공개 필드의 업무 값은 기존 게임 DB에서 읽고 수집 메타데이터는 명령이 작성한다. 공개 상태의 소비 검증은 후속 광고 교시 책임이다.

광고 작업 폴더에서 수신할 경로는 `../Game-server/data/exports/player-cdc.ndjson`이다. [저장 경로 정정 기록](../../../../../../handoffs/2026-10-08-day24-data-path-correction.md)을 따른다.
