# README.md

게임 서버의 현재 실행·폴더 구조와 과거 수업 반영 기록을 설명한다. config는 프로젝트 루트에 있고 manage.py·가상환경·game 앱은 server 아래에 있다. 2026-10-08 현재 진행 안내를 앞에 두고 기존 10/11일차 안내를 당시 작업 이력으로 구별한다.

24일차는 게임의 `export_player_snapshot` 관리 명령과 공식 1교시 검사 12개 통과·0개 실패, 실제 루트 `data/exports/player-cdc.ndjson`의 56행·13,275 bytes를 안내한다. `server/data`는 없으며 출력의 상대 경로는 실행 폴더 기준이므로 저장소 루트에서 `python server/manage.py export_player_snapshot --output data/exports/player-cdc.ndjson`을 실행한다. 원본은 이미 존재한다. 광고 소비 경로는 `../Game-server/data/exports/player-cdc.ndjson`이고 2교시는 `ads/snapshot_intake.py` 문제틀 작성 중으로 완료되지 않았으며 3~8교시는 미적용이다. 초기 실패 기록과 수정 후 성공 결과를 구별하고 `docs/server-routing/day24-progress.md` 및 경로 정정 인수인계에 연결한다.

최신 23일차 3교시 직접 구현 위치는 server/game/ad_gateway.py::request_ad_event 본문이다. Player 기반 payload, events API 호출, 거절/성공 응답 검증을 안내한다. 누락된 call_ads를 같은 파일에 보충했고 기존 request_decision·combined ad_views·URL·서버 설정을 보존했다는 실제 구현 상태를 설명한다.

공식 검증 파일은 config/check_day23_period3.py로 저장하도록 안내한다. 현재 다운로드가 로그인 페이지로 이동해 미저장·미실행이며, 자체 계약 검사·기존 게임 테스트·원문 AST 비교 결과와 구별한다. 문서의 실행 명령은 Game-server 루트에서 server/.venv/Scripts/python.exe를 사용한다.

이 파일은 설명 문서이므로 함수·메서드 시그니처와 반환값은 없다. 명령의 대상·기본값은 실제 관리 파일·기존 설정이 소유하며 README를 읽는 것으로 DB 조회·변경이 발생하지 않는다. 비밀값·쿠키·세션·CSRF 토큰을 기록하지 않는다.
