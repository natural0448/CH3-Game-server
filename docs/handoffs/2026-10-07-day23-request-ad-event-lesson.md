# 2026-10-07 · 최신 23일차 3교시 request_ad_event 정합화

> 2026-10-07 검토 주석: 아래는 해당 작업 시점의 결과를 보존한 이력입니다. 교안 버전·적용 범위·검사 수는 최신 상태와 다를 수 있습니다. [차이와 현재 상태](../../../ad_server/docs/server-routing/reviews/2026-10-07-lesson-deviations.md).

## 요청과 결과

최신 「현재 ad_server에서 노출·클릭과 광고주 보고서 완성하기」의 3교시 직접 구현을 적용했다. 대상은 `server/game/ad_gateway.py::request_ad_event()` 본문 세 구간이다. 앞서 안내했던 접속기 작업과 게임 테스트 파일 추가를 이번 교시의 핵심으로 취급하지 않는다.

함수 본문은 교안 HTML의 전체 완성 코드와 AST가 동일하다. 로그인 Player 기반 payload, events API의 상태/JSON 반환, 거절/성공 응답 검증을 그대로 적용했다. 현재 파일에는 `call_ads()`가 없었으므로 같은 파일에 JSON POST·두 매체 헤더·3초 timeout을 보충하고 교안 2교시 diff의 HTTPError 처리를 적용했다. 기존 `request_decision()`, AdsUnavailable, import, 로그인 view, URL, 설정은 보존했다. 중계 view는 현재 combined `ad_views.ad_event` 구조를 유지했다.

## 시작 Git 상태와 기존 변경

Chapter3: `Git 상태 확인 불가: 저장소 아님`. 상위 폴더 조회는 권한 제한으로 확인하지 못했다. Git 초기화·stage·commit은 수행하지 않았다.

Game-server 직전 커밋은 `6aa5329 22일차 - 진행사항 반영`, staged 없음. 기존 unstaged 개발 파일은 `server/game/ad_gateway.py`, `ad_views.py`, `test_ads.py`, `urls.py`였고 해당 짝 문서와 라우팅 색인 변경도 존재했다. 기존 untracked에는 앞선 23일차 인수인계와 검증 기록이 있었다. Game-client 직전 커밋은 `2dd8d97 22일차 내용 반영`, staged 없음. README와 client/application/network/ui/contracts 및 tests의 기존 변경을 보존했다.

시작 시 staged·unstaged·untracked의 전체 목록은 [start.json](../server-routing/verification/day23-request-ad-event/start.json)에 기록했다. 이 목록은 작업 시작 전에 존재한 변경이며 이번 작업으로 주장하지 않는다. 겹치는 파일의 변경 전 사본과 SHA-256은 같은 폴더 `before/`에 보존했다. `.env`는 값을 복사하지 않고 해시만 대조해 변경되지 않았음을 확인했다.

## 이번 변경 파일

- `server/game/ad_gateway.py`: 사건 본문을 교안 완성 코드와 일치시키고 누락된 call_ads 전제를 보충.
- `server/game/test_ads.py`: 기존 사건 성공 응답 fixture에 status=200을 부여. 기존 assertion 유지.
- `docs/server-routing/files/server/game/ad_gateway.py.md`: 최종 함수 계약·호출·반환·설정 출처.
- `docs/server-routing/files/server/game/test_ads.py.md`: HTTP fixture 적응 및 selection 반환 설명.
- `docs/server-routing/README.md`: 최신 3교시 범위와 검증 상태.
- `README.md`: 서버의 수정 위치와 공식 검증 파일 실행 안내.
- `../Game-client/README.md`: 기존 접속기 연결 자료를 최신 3교시 직접 구현과 구별하도록 제목·도입·실행 안내 정정. 클라이언트 코드 변경 없음.

새 실행 코드·설정·테스트 파일 추가, 이동, 삭제는 없다. 추가 기록은 본 인수인계와 `verification/day23-request-ad-event/`다. 변경 전후 구분은 [changes.json](../server-routing/verification/day23-request-ad-event/changes.json)에 있다.

## 책임 경계와 문서 정합화

로그인 Player 조회와 HTTP 400/503 변환은 기존 `ad_views.ad_event`, Player 기반 사건 대상·상태/receipt 검증은 `request_ad_event`, 서버 키 헤더·JSON 전송·공개 오류 정규화는 `call_ads`의 책임이다. 선택 snapshot과 사건 DB 저장은 기존 광고 서버가 맡는다. 이 작업의 합성 검사는 실제 노출이나 DB 사건을 만들지 않는다.

코드 검증 후 별도의 문서 정합화 단계를 수행했다. 변경한 개발 파일 두 개의 짝 문서만 갱신했고 색인의 최신 교시 안내를 수정했다. call_ads의 실제 시그니처·파라미터·반환·의사코드·직접 호출·값 출처를 포함했다. 새 소스 경로가 없으므로 새 색인 행은 필요하지 않았다.

## 검사 명령과 결과

교안 HTML에서 완성 코드를 추출해 실제 request_ad_event와 AST를 대조했다: PASS. 기존 request_decision과 AdsUnavailable도 시작 사본과 AST가 동일했다. [source-comparison.json](../server-routing/verification/day23-request-ad-event/source-comparison.json)을 따른다.

교안 계약 표를 실제 함수에 적용한 독립 검사 24개: PASS. 설정과 call_ads 반환만 합성 값으로 대체했다. 새/중복 사건, 허용 오류 5개, 목록/문자열 거절, 503, 잘못된 성공 응답, 잘못된 입력, 빈 매체 키를 확인했다. Player 7을 999로 바꾼 메모리 내 함수 복사본의 대상 불일치도 감지했다. 실제 소스에는 이 오답을 저장하지 않았다. 이유: 로그인 Player와 선택 결정에 저장된 대상이 달라져 같은 사용자의 사건으로 연결할 수 없다. [contract-checks.json](../server-routing/verification/day23-request-ad-event/contract-checks.json)을 따른다. 이 검사는 공식 검증기의 실행 결과로 주장하지 않는다.

게임 회귀검사 20개: PASS. Game-server 폴더에서 아래와 같이 config를 메모리 SQLite로 대체해 실행했다. 실제 MySQL 설정 파일·데이터는 수정하지 않았다.

```powershell
@'
import sys, os
from pathlib import Path
root=Path.cwd()
sys.path[:0]=[str(root),str(root/'server')]
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
from config import settings
settings.DATABASES={'default': {'ENGINE':'django.db.backends.sqlite3','NAME':':memory:'}}
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py','test','game.test_ads','game.tests','--verbosity','1'])
'@ | .\server\.venv\Scripts\python.exe -X utf8 -B -
```

라우팅 감사는 다음 명령으로 시작/최종 상태를 검사했다.

```powershell
python -X utf8 -B C:\Users\이해나\.codex\skills\routing-doc-auditor\scripts\audit_routing.py --repo C:\MLO01-01\Chapter3\Game-server --routing-dir docs/server-routing --format json --output C:\MLO01-01\Chapter3\Game-server\docs\server-routing\verification\day23-request-ad-event\final-audit.json
```

시작 감사 PASS. 최종 감사 Python 4개·시그니처 21개, issue 0, summary.ok=true. 결과는 같은 경로의 `final-audit.json`에 있다. Game-server와 Game-client의 `git diff --check`도 PASS이며 줄끝 변환 안내만 있었다. 최종 staged 없음, 커밋 unchanged, 기존 변경과 이번 변경 구분은 `git-final.json`과 `changes.json`에 기록했다.

## 미실행과 다음 순서

교안의 공식 `check-ad-event-logic.py` 다운로드는 praxolve.net의 로그인 페이지로 이동했다. 브라우저 목록에도 인증된 교안 탭이 없었다. 로그인 HTML을 Python 검증 파일로 저장하거나 임의 검증 파일로 대체하지 않았다. 공식 `config/check_day23_period3.py`는 미저장·미실행이다. 실제 게임 프로세스 재시작이나 화면 클릭은 이번 함수 작성의 검증 결과로 주장하지 않는다.

로그인한 교안의 [공식 검증 파일](https://praxolve.net/encore/mlops2026/chapters/chapter-3/days/day-23/lessons/encore.chapter3.game-mongo-analytics/embed-content/assets/day23-period3/check-ad-event-logic.py)을 `Game-server/config/check_day23_period3.py`로 저장한 뒤 실행한다. 기존 `config/settings.py`는 유지한다.

```powershell
Set-Location C:\MLO01-01\Chapter3\Game-server
.\server\.venv\Scripts\python.exe config/check_day23_period3.py
```

실패하면 해당 검사 이름과 request_ad_event의 세 구간을 대조한다. 서버 진행 안내는 Game-server/README.md에도 기록했다.
