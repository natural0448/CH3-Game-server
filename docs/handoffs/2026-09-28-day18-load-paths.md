# 18일차 측정 도구 경로 정합화 인수인계

## 요청 목적과 완료 결과

`Game-server/server`, `Game-server/tools`, `Game-server/data` 구조에서 4교시 측정 명령의 상대경로가 실행 위치에 따라 다른 폴더를 가리키는 문제를 수정했다. `tools/ws_load.py`와 `tools/read_load_result.py`는 이제 `data/...`와 `../data/...`를 모두 `Game-server/data/...`로 해석한다. 인증·WebSocket·게임 상태 계약은 변경하지 않았다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `ed45ba4 day17-finish`
- staged 변경: 없음
- 작업 시작 전에 존재한 변경:
  - 수정: `server/game/urls.py`, `server/game/views.py`
  - untracked: `server/game/management/commands/prepare_load_players.py`, `tools/read_load_result.py`, `tools/ws_load.py`
- 위 기존 파일은 사용자 작업으로 취급했다. 서버 인증 파일의 내용을 되돌리거나 재구성하지 않았다.

## 이번 작업 변경 파일

수정:

- `tools/ws_load.py`: 프로젝트 루트 기반 데이터 경로 해석, 파일 오류 메시지, 경로·interval 도움말 추가.
- `tools/read_load_result.py`: 같은 경로 해석과 파일 오류 처리, `main()` 진입점 추가.
- `docs/server-routing/README.md`: 이번 변경 파일과 작업 시작 전에 변경되어 있던 서버 파일의 1:1 문서 색인 추가.

추가:

- `docs/server-routing/files/tools/ws_load.py.md`
- `docs/server-routing/files/tools/read_load_result.py.md`
- `docs/server-routing/files/server/game/management/commands/prepare_load_players.py.md`
- `docs/server-routing/files/server/game/urls.py.md`
- `docs/server-routing/files/server/game/views.py.md`
- 이 인수인계 문서.

## 설계 결정과 책임 경계

- `PROJECT_DIR`은 각 도구 파일의 `tools` 부모로 계산한다.
- 절대경로는 그대로 사용한다.
- 선두 `.` 또는 `..`를 제외한 첫 경로가 `data`이면 `PROJECT_DIR/data/...`로 고정한다.
- 그 밖의 상대경로는 기존처럼 현재 작업 디렉터리를 기준으로 한다.
- 비밀번호는 계속 `getpass`로만 받고 경로 오류나 결과 파일에 포함하지 않는다.
- 서버 URL, 인증 view 선택, WebSocket 명령과 게임 규칙은 바꾸지 않았다.

## 라우팅 문서 정합화

변경되거나 작업 시작 시 이미 변경되어 있던 개발 파일 5개에 대해 1:1 짝 문서를 만들고 `docs/server-routing/README.md`에 등록했다. 함수 시그니처, 파라미터, 의사코드, 직접 호출, 주요 변수 출처를 현재 구현에 맞췄다.

## 실행한 검사

```text
python -m py_compile tools/ws_load.py tools/read_load_result.py server/game/management/commands/prepare_load_players.py
결과: 성공

python tools/ws_load.py --help
python tools/read_load_result.py --help
결과: 성공, 경로와 interval 도움말 확인

Game-server 및 Game-server/server에서 resolve_project_path 검사
결과: data/load/accounts-20.json과 ../data/load/accounts-20.json 모두 Game-server/data/load/accounts-20.json으로 해석

python manage.py check
결과: System check identified no issues

python manage.py test game.test_delivery
결과: 14 tests passed

임시 측정 JSON을 read_load_result.py로 루트·server 양쪽에서 읽기
결과: 세 경로 형태 모두 동일한 지표 출력, 임시 파일 삭제 완료
```

## 실행하지 못한 검사와 남은 위험

- 학습 계정 공통 비밀번호를 알지 못하므로 실제 두 계정 로그인·WebSocket 10초 측정은 실행하지 않았다.
- 작업 당시 8000, Spark 7077/7078/7079와 Kafka 9096은 열려 있었지만 Kafka 9092/9094는 열려 있지 않았다. 이 상태는 4교시 전체 인프라 조건과 다르며 이번 경로 수정 범위에서는 프로세스를 재시작하지 않았다.
- `server/game/urls.py`의 뒤쪽 인증 경로 두 개는 앞쪽 `game.auth_views` 경로에 가려진 기존 사용자 변경이다. 이번 작업에서는 보존했다.

## 다음 실행 순서

`Game-server` 루트에서 다음을 실행한다.

```powershell
.\server\.venv\Scripts\python.exe .\tools\ws_load.py --accounts .\data\load\accounts-20.json --clients 2 --seconds 10 --interval 1 --output .\data\load\run-02.json
.\server\.venv\Scripts\python.exe .\tools\read_load_result.py .\data\load\run-02.json
```

첫 명령에서 계정 준비 때 사용한 공통 비밀번호를 입력한다. `day18_001`, `day18_002`로 실행 중인 GUI 접속기는 먼저 닫는다.
