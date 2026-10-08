# 2026-10-07 · 22일차와 수정23일차1·2교시 교안 정합화

> 2026-10-07 검토 주석: 아래는 해당 작업 시점의 결과를 보존한 이력입니다. 교안 버전·적용 범위·검사 수는 최신 상태와 다를 수 있습니다. [차이와 현재 상태](../../../ad_server/docs/server-routing/reviews/2026-10-07-lesson-deviations.md).

## 요청과 완료 결과

교안을 정본으로 스크립트를 맞추고 기존 폴더·환경을 유지하라는 연속 요청을 수행했다. 최신 정본은 Desktop의 「현재 ad_server에서 노출·클릭과 광고주 보고서 완성하기.html」 v2.3이다. 이전23일차 교안과 교시 구성이 달라1교시 입찰 반환·snapshot·색인,2교시 사건 API·오류 전달·광고주 선택/실적 화면으로 갱신했다.22일차 실습 정본도 현재 환경에서 실행하도록 맞췄다.

## 작업 시작 전 Git 상태

직전 커밋: 6aa5329 22일차 - 진행사항 반영. 기존 변경은 전부 작업 시작 전에 존재한 변경으로 취급했다.

### 기존 staged

```text
없음
```

### 기존 unstaged

```text
M	docs/server-routing/README.md
M	docs/server-routing/files/server/game/ad_gateway.py.md
M	docs/server-routing/files/server/game/ad_views.py.md
M	docs/server-routing/files/server/game/test_ads.py.md
M	docs/server-routing/files/server/game/urls.py.md
M	server/game/ad_gateway.py
M	server/game/ad_views.py
M	server/game/test_ads.py
M	server/game/urls.py
```

### 기존 untracked

```text
docs/handoffs/2026-10-07-day23-period01-02-sync.md
docs/server-routing/verification/day23-final-audit.json
docs/server-routing/verification/day23-start-audit.json
docs/server-routing/verification/lesson-align-start-audit.json
```


기존 소스/작업 전 상태: `ad_server/docs/server-routing/verification/lesson-alignment/start.json`과 `before/`. .env는 원본 사본 대신 해시만 저장했다. 값을 diff/문서에 복사하지 않았다.

## 이번 작업 변경 파일

- modified: `server/game/ad_gateway.py`
- modified: `server/game/ad_views.py`
- modified: `server/game/test_ads.py`

추가/수정만 수행했으며 개발 파일 이동·삭제는 없다. 상세 경계는 공통 `changes.json`에 시작 해시와 최종 해시로 구분했다. Git HEAD diff 전체를 이번 작업으로 주장하지 않는다. Game-server의 game/urls.py, Game-client의 app/UI 등에는 작업 전 변경이 계속 존재한다. Client의7개 수정은 최신 교안 수신 전 같은 연속 작업에서 수행한 상태이며 새 교안 수신 후 추가 클라이언트 기능을 작성하지 않았다.

## 설계와 교안 대응

- 기존4인수 choose_ad와 bid_amount Mongo 스키마·PNG·slots·계정·env·DB를 유지한다.3인수/bid_units 예제에 맞춘 전면 재구성은 하지 않았다.
- save_bid가 자기 소유 bids 문서를 반환한다. 새 결정에는 승자 owner_user_id와 UTC BSON Date selected_at을 추가했다. event_time은 동일 시각 ISO이며 후보/소재/맥락은 당시 snapshot이다. 과거 결정은 보정하지 않았다.
- events.py는 수정 CODE15이고 비문자열 종류 타입 검사만 추가했다. clean_subject는 실제 services helper다. 점 표기 수신자 조회, 당시 후보 검증, 선행 노출, 최초 사건 유지, 허용한 오류 코드가 적용됐다.
- 기존 media_auth.read_media_body를 유지하며 두 헤더 검사와 media_api_methods를 추가했다. 키 출처는 기존 서버 설정이다. 인증401/입력400/장애503, 사건 성공no-store, 기존 게임/광고주 CSRF를 유지한다.
- 기존 combined ads/views.py에서 매체 event_view와 광고주 advertiser_event_view를 사용한다. 기존 루트 include 구조의 ads/urls.py에 web-events를 추가했다. game/ad_views.py·game/urls.py의 기존 실제 경로를 유지했다. unused web_views/media_urls/ad_events 중복 모듈을 만들지 않았다.
- 광고주 events 표는 자기 owner 결정만 selected_at 역순 최대30개다. 조회는 사건을 만들지 않고 미기록 상태를 표시한다. 교안 표·빈 안내를 기존 base 디자인에 연결했으며 미구현6교시 reports 링크는 추가하지 않았다.
- 현재 Pygame 자동 노출·클릭은 이전 작업에서 이미 존재하며 수정 교안의3교시다. 기능을 보존하고 서버 계약 회귀검사를 수행했다. NDJSON/집계/일별 보고서/전달은 미적용이다.
- 새 config/day23-subject.py, day23-period-01.py, day23-period-02.py, create_ad_indexes 명령은 교안 전체 코드 그대로다. 기존 ensure_ad_event_indexes 명령과 수동 관찰 파일은 보존 자료다. 수정 교안에서는 Django shell 수동 사건 실습을 수행하지 않는다.
- 기존 게임 서버8000의 확인한 수업 프로세스만 재시작했다. 광고8001은 autoreload로 반영됐고 실제 경로/인증 실패 응답을 확인했다. 인프라 재설치/replicaSet 초기화/DB 재설정/계정 변경은 하지 않았다.

## 라우팅 문서 정합화

코드 검증 후 별도 단계에서 이번 변경 파일의 짝 문서를 갱신하고 해당 색인을 맞췄다. 변경하지 않은 파일의 짝 문서를 일괄 재생성하지 않았다.

- `docs/server-routing/files/server/game/ad_gateway.py.md`
- `docs/server-routing/files/server/game/ad_views.py.md`
- `docs/server-routing/files/server/game/test_ads.py.md`
- 색인: `docs/server-routing/README.md`

검사 결과: ad_server21개 개발 파일(18Python) scoped AST·짝·색인 통과. Game-server Git 변경4Python/20symbols, Game-client12Python/88symbols 검사 통과. Client 전체77파일/77짝 문서도 통과했다. 단순 시그니처 외 파라미터·반환·의사코드·직접 호출·상태 출처도 최종 구현에 맞췄다.

## 실행한 검사

- ad_server: `python tools/verify_lesson_alignment.py` → 수정 정본 AST/실습/실적 표23개 대조 PASS.
- ad_server: `python tools/verify_day22.py --mongod "C:/Program Files/MongoDB/Server/8.3/bin/mongod.exe"` → 광고37테스트 PASS/skip0, 별도 Mongo27107·테스트SQLite.
- Game-server: config.settings.DATABASES를 Django setup 전에 memory SQLite로 override하고 game.test_ads/game.test_history 실행 →13테스트 PASS; 실제 MySQL 연결/변경 없음.
- Game-client: SDL_VIDEODRIVER=dummy, SDL_AUDIODRIVER=dummy, `python -B -m unittest discover -s tests` →50테스트 PASS.
- ad_server: `python tools/verify_day23.py --mongod "C:/Program Files/MongoDB/Server/8.3/bin/mongod.exe"` → 분리Mongo27109·HTTP18000/18001·SQLite·SDL dummy에서 기존 두 슬롯 HTTP/PNG/모의 클릭, 최초/재전송/당시금액/사건4건 PASS. 증거 폴더 day23-period02라는 이전 이름은 유지하되 최신 교안3교시 기존 기능 회귀검사로 구분했다.
- 세 config 기초 파일 출력: 중첩 사전/7,40 30, sample-decision:impression/click. 실제 create_ad_indexes 두 번 출력decision_event_once; Django check PASS.
- 실행 서버 광고주 events 로그인 redirect, 광고/게임 events GET405, 두 매체 헤더 없는 요청401/media_auth_required. 실수업 사건 생성 없음.
- Git 저장소 두 곳 routing-doc-auditor·git diff --check PASS, Client tools/check_routing_docs.py PASS, non-Git 광고 scoped auditor PASS.
- 이전22일차 연결/CRUD/정산 모형의 격리 실행 증거는 scripts.json에 보존(옆 문서 유지, 자기 practice ID만 삭제, charge22/balance78).

근거: 공통 `ad_server/docs/server-routing/verification/lesson-alignment/`의 source-comparison.json, test-results.json, live-readiness.json, final-audit.json, git-final.json 및 각 Git 프로젝트의 lesson-align-final-audit.json.

## 미실행·한계·후속

- 실제 학생이 Compass/Pygame 창에서 관찰한 화면·클릭은 not_run이다. fixture/모의 클릭을 실수업 증거로 주장하지 않는다.
- 기존에 owner_user_id/selected_at 또는 후보 당시 정보가 없는 과거 결정은 자동 수정하지 않았다. 새 광고 선택이 필요하다. 표가 비어도 현재 광고주의 캠페인이 승자가 아닌 경우 정상이다.
- 수정 교안3교시 이후의 별도 신규 적용은 하지 않았다. 기존 접속기의15초 재요청은 유지했고 교안에서 전제한10초 표시 유지 타이머는 기존 코드와 차이가 있어3교시 검토 항목이다.
- Game-server/Client의 작업 전 변경과 Git untracked 문서는 그대로 유지했다. staged/commit/push는 수행하지 않았다. ad_server는 Git이 없어 시작/최종 hash 기준으로 구분한다.

## 다음 실행·확인 순서

광고 폴더에서 다음을 실행한다. 이미 두 서버가 실행 중이면 중복 runserver를 켜지 않는다.

```powershell
Set-Location C:\MLO01-01\Chapter3\ad_server
.\.venv\Scripts\Activate.ps1
python config/day23-subject.py
python config/day23-period-01.py
python config/day23-period-02.py
python ad_config/manage.py create_ad_indexes
```

브라우저 http://127.0.0.1:8001/advertiser/events/ → 기존 광고 계정 로그인 → 기존 게임 접속기에서 광고 새로 요청 → 선택/실적 표 새로고침. Compass는 기존27017의 village_ads → decisions → Sort {"selected_at": -1}로 새 owner/chosen/candidates snapshot을 확인한다. 사건을 직접 shell에서 생성하지 않는다.

## 최종 상태

Git 최종 상세는 git-final.json에 저장했다. 기존 staged 없음 유지, 이번 변경은 working tree/로컬 파일에만 존재한다. 기존 서버 env 해시 불변을 재확인했다. 수업 캠페인·입찰·사건 문서를 변경하지 않았다. 완료 후 인수인계 파일 자체가 untracked 항목에 추가될 수 있으며 이는 문서 작업이다.
