# 17일차 1교시 준비 인수인계

## 요청 목적과 완료 결과

17일차 1교시를 현재 Game-server에서 바로 시작할 수 있도록 Django·Python·기존 데이터 상태를 확인하고, 최근 확정 사실의 `player_id`, `command_id`, `event_id`를 제한된 공개 필드로 읽는 `inspect_game_facts` 명령을 추가했다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `e24b87e 15day - 6교시`
- staged 변경: 없음.
- 기존 변경: 15~16일차 Kafka/Spark/NiFi 설정·명령·문서, 시간 창 API, 실행 안내 변경과 여러 untracked 산출물이 있었다.
- 이번 준비는 기존 변경을 되돌리거나 정리하지 않았고, 새 명령과 짝 문서 및 색인만 추가했다.
- 작업 중 사용자가 만든 것으로 보이는 빈 `server/analytics/management/commands/inspect_game_facts.py`가 새로 나타났다. 사용자 파일로 보존했으며 Django 등록 결과는 `game` 앱의 명령이다.

## 이번 작업 파일

- 추가: `server/game/management/commands/inspect_game_facts.py`
- 추가: `docs/server-routing/files/server/game/management/commands/inspect_game_facts.py.md`
- 수정: `docs/server-routing/README.md`
- 추가: 이 인수인계 문서.

삭제·이동한 파일은 없다.

## 설계 결정과 책임 경계

- QuerySet을 정렬한 뒤 먼저 slice하여 3·5·10행만 DB에서 읽는다.
- 출력은 식별자, 사건·발행 시각, payload 키 이름과 transition 존재 여부로 제한한다. payload 값 전체는 출력하지 않는다.
- 조회는 GameEvent, Player, 세션이나 게임 version을 변경하지 않는다.
- Kafka offset은 이 ORM 명령의 필드가 아니며 이후 Kafka 봉투/Delta 입력에서 전달 위치로 확인한다.
- Delta 패키지와 스트리밍 코드는 1교시 준비 범위에서 설치하거나 실행하지 않았다.

## 환경 확인

- Python 3.12.13
- Django 5.2.17
- `manage.py check`: 통과
- 기존 `GameEvent`: 존재
- 최근 사실: `player.moved`, command_id 존재, player_id 존재

## 라우팅 문서

새 개발 파일과 `docs/server-routing/files/server/game/management/commands/inspect_game_facts.py.md`를 1:1로 연결하고 `docs/server-routing/README.md`에 색인을 추가했다.

## 검사 결과

- `py_compile`: 통과.
- `manage.py check`: 통과.
- `manage.py help inspect_game_facts`: 명령과 `--rows {3,5,10}` 로딩 확인.
- Django `get_commands()` 등록 앱: `game`.
- `--rows 3`: 3행 출력.
- `--rows 5`: 5행 출력.
- 두 실행의 최근 3행 순서와 event_id가 일치.
- 각 JSON 행은 문서화한 공개 필드만 포함.
- `git diff --check`: 오류 없음. 기존 CRLF 변환 예고만 출력.

## 실행 및 확인 순서

```powershell
cd C:\MLO01-01\Chapter3\Game-server\server
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py help inspect_game_facts
.\.venv\Scripts\python.exe manage.py inspect_game_facts --rows 3
.\.venv\Scripts\python.exe manage.py inspect_game_facts --rows 5
```

3행과 5행 조회는 표시 상한만 바꾸며 새 사실을 생성하지 않는다. 새 사실이 필요한 관찰 단계에서는 사용자가 접속기에서 정상 이동을 한 번 수행한 후 명령을 다시 실행한다.

## 남은 범위

2교시 이후의 원문 projection, Delta 스트리밍 파일, JVM Delta package 제출은 아직 적용하지 않았다. 교안 순서를 따라 별도 작업으로 진행한다.

## 사용자 작성 내용 반영

사용자가 `server/analytics/management/commands/inspect_game_facts.py`에 먼저 작성한 `published_at`, `payload_keys`, `has_transition` projection을 실제 Django가 등록하는 `server/game/management/commands/inspect_game_facts.py`에 반영했다. 원래 사용자 파일은 삭제하지 않았다.
