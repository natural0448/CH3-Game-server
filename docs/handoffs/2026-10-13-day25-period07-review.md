# 25일차 7교시 게임 연결 검토 · 2026-10-13

**후속 수정 완료:** 아래 최초 검토는 수정 전 기록이다. 현재 구현·검증·추가 파일 정리 상태는 이 문서 마지막의 후속 수정 항목을 따른다.


사용자의 누락 확인 요청으로 현재 게임 변경을 검토했다. HEAD=04bafae day25 - chapter1, 시작 staged/untracked 없음, unstaged=server/game/ad_gateway.py·server/game/urls.py다. 두 파일은 작업 시작 전 사용자 변경이며 원문을 보존했다. Chapter3 상위는 Git 저장소가 아니다. [시작 기록](../server-routing/verification/2026-10-13-day25-period07-review/start.json)을 따른다.

request_context와 request_decision은 25일차 제공 완성 코드 AST와 같다. URL이 참조한 ad_views.ad_context는 ad_views/views 모두에 없어 **server/.venv의 manage.py check가 AttributeError로 실패**한다. play/events의 중복 URL도 보존했다. 광고 인증의 본문 media_id 계약과 조회 payload, 광고 URL include/callable 이름도 연결되지 않았다. 본인 조회·새 결정 두 건의 통합 성공을 기록하지 않는다. 책임 경계와 수정 미적용 부분은 [광고 검토 전체 기록](../../../ad_server/docs/handoffs/2026-10-13-day25-period07-review.md)에 있다.

개발 소스·설정·게임 data·Mongo 프로세스를 수정하지 않았다. 이번 수정은 docs/server-routing/files/server/game/ad_gateway.py.md·urls.py.md·README.md이고, 새 파일은 이 handoff와 verification/2026-10-13-day25-period07-review 기록이다. 함수·파라미터·반환·직접 HTTP 호출과 실패하는 URL 선언을 실제 코드로 정합화했다. 마감에서 두 소스 SHA와 Git 기존/이번 문서 변경을 구분하고 표준 routing-doc-auditor를 재실행한다.

광고 가상환경으로 최초 게임 check를 시도해 daphne 부재로 실패한 것은 검사 환경 선택 오류다. 실제 게임 server/.venv에서 재검사한 결과 위 AttributeError가 확인됐다. 의존성을 설치하거나 기존 가상환경을 변경하지 않았다. 관련 AST·Django 체크·실제 읽기 probe 기록은 광고 verification/2026-10-13-day25-period07-review에 있다. 게임 CLI와 source 보존 결과는 [게임 마감](../server-routing/verification/2026-10-13-day25-period07-review/finish.json)을 따른다.

다음 단계는 누락 함수와 URL을 현재 파일 분리에 맞게 연결하는 코드 수정이며 **미적용**이다. 수정 후 사용자 VS Code의 별도 터미널에서 실행한다.

```powershell
Set-Location C:\MLO01-01\Chapter3\Game-server\server
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py runserver 127.0.0.1:8000
```

현재 check 실패 상태에서는 runserver를 정상 기동했다고 판단하지 않는다. 전체 양쪽 서버 확인·본인 context·화면 decision ID 관찰 순서는 광고 인수인계를 따른다. 8교시 구현, 새 Player/decision 생성, DB 복구는 이번 검토 범위 밖이다.


## 후속 수정 · 기존 파일 안에서 완료

server/game/views.py에 제공 ad_context와 필요한 imports만 추가하고 server/game/urls.py의 누락 참조를 views.ad_context로 맞췄다. server/game/test_ads.py에 PlayerContextTests를 통합했다. 기존 gateway·ad_views·게임 data·중복 URL은 보존했다. 별도 test_ad_context.py는 제거했다. 실제 게임 환경의 check와 context/사건 검사6개가 성공했다. 소스 시작/종료 분류와 마감 검사는 기존 verification/2026-10-13-day25-period07-review/start.json·finish.json의 followup_fix를 따른다.

views/urls/test_ads 기존 짝 문서와 README를 최종 코드로 정합화했고 gateway 문서의 이전 장애 설명도 정정했다. 새 문서 파일을 생성하지 않았다. 시작에 만든 verification/2026-10-13-day25-period07-fix 기록 폴더 삭제는 자동 승인 심사의 명시적 기록 삭제 승인 부재 사유로 처음 거절됐다. 이후 사용자 명시적 승인으로 경로·목록·해시를 재대조하여 삭제 완료했다. 우회 삭제하거나 게임 서버 프로세스를 중지하지 않았다. 해당 경로/보존 상태와 광고 인증·본인 조회·기존 파일만 사용하는 명령은 광고 인수인계의 후속 항목을 따른다.


후속 마감에서 사용자가 작업 중 일부 게임 변경을 staged한 것을 확인했다. 이미 삭제된 에이전트 생성 테스트 파일/검증 사본 여섯 항목도 인덱스에 남아 있어, 생성 당시 내용과 Git CRLF/LF 정규화의 동일성을 확인한 뒤 해당 경로만 git rm --cached로 제거했다. 첫 sandbox 시도는 index.lock 쓰기 권한이 없어 실패했고 승인된 cleanup 범위의 sandbox 밖 실행으로 완료했다. 다른 사용자 staged 코드/문서 항목은 보존했고 add/commit/reset을 수행하지 않았다. 마지막 Git HEAD·staged/unstaged 분류와 생성 경로의 인덱스 잔존 여부는 finish.json의 followup_fix가 기준이다.
