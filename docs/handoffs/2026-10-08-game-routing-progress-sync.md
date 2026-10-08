# Game-server 현재 진행 라우팅 문서 정합화 · 2026-10-08

## 요청 목적과 완료 결과

사용자가 현재까지 진행사항에 따른 라우팅 문서 갱신과 서브에이전트 활용을 요청했다. 이 문서는 Game-server를 담당한 서브에이전트의 수행 기록이다. 기존 코드를 기준으로 22일차 이미지 광고 연결, 23일차 광고 사건 중계, 24일차 1교시 공개 snapshot까지의 실제 호출 경계와 진행 상태를 문서화했다. **코드·설정·데이터의 동작은 변경하지 않았다.**

24일차 현재 공식 1교시 검사 결과는 **12개 통과·0개 실패**다. 실제 원본은 `Game-server/data/exports/player-cdc.ndjson`이며 56행·13,275 bytes이고 `server/data`는 없다. 이후 부모의 최신 관찰에 따라 광고 `ads/snapshot_intake.py`는 **2교시 문제틀 작성 중·미완료**, 3~8교시는 **미적용**으로 반영했다. 초기 1교시 실패와 이후 사용자 수정 후 성공 결과를 현재 페이지에서 구별했고 과거 검토·증거는 수정하지 않았다.

## 작업 시작 전 Git 상태

`C:/MLO01-01/Chapter3`는 **Git 상태 확인 불가: 저장소 아님**이다. Git을 초기화하지 않았다. 대상은 독립 저장소 `C:/MLO01-01/Chapter3/Game-server`이며 직전 커밋은 `5fd757d day23 진행사항`이다. 하위 AGENTS.md는 검색에서 발견되지 않아 Chapter3/AGENTS.md를 적용했다.

| 시작 구분 | 작업 시작 전에 존재한 변경 |
|---|---|
| staged | 없음 |
| unstaged | `.gitignore`, `docs/server-routing/README.md` |
| untracked 개발 파일 | `server/game/management/commands/export_player_snapshot.py`, `tools/check_day24_logic.py` |
| untracked 짝 문서 | `docs/server-routing/files/.gitignore.md`, `files/data/exports/player-cdc.ndjson.md`, `files/server/game/management/commands/export_player_snapshot.py.md`, `files/tools/check_day24_logic.py.md` (`files/`는 docs/server-routing 아래) |
| untracked 기존 인수인계 | `docs/handoffs/2026-10-08-day24-period01-review.md`, `docs/handoffs/2026-10-08-day24-data-path-correction.md` |
| untracked 기존 검증 기록 | `docs/server-routing/verification/day24-period01-review/`와 `day24-data-path-correction/`의 기존 증거 파일. 정확한 개별 목록은 시작 기록에 보존 |

부모 에이전트가 이번 요청의 정확한 시작 목록·보호 대상 해시를 `docs/server-routing/verification/day24-routing-sync/start-state.json`에 저장했다. 서브에이전트의 작업 시작 확인은 `agent-state-start.json`에도 있다. 후자는 최초 AST 검사가 만든 agent-* 증거가 포함되므로 기존 변경의 기준은 부모의 start-state.json이다. 기존 모든 변경을 작성자 추정 없이 **작업 시작 전에 존재한 변경**으로 취급했다. `.gitignore`와 사용자 Python 및 기존 untracked 문서를 이번 작업의 코드 추가로 주장하지 않는다.

## 이번 작업에서 바꾼 파일

| 구분 | 파일 | 변경 목적 |
|---|---|---|
| 수정 | `README.md` | 2026-10-08 진행 상태·올바른 루트 data 경로·공식 성공 결과를 앞에 추가하고 초기 수업 기록과 구별 |
| 수정 | `docs/server-routing/README.md` | 기존 사용자 항목을 보존하며 현재 진행 페이지와 인수인계 연결, 게임 HTTP 색인의 광고 경로 책임 보충 |
| 수정 | `docs/server-routing/files/README.md.md` | README의 현재 상태·실행 위치·미적용 범위와 1:1로 정합화 |
| 수정 | `docs/server-routing/files/server/game/urls.py.md` | 실제 광고 preview/decision/events 경로를 순서대로 반영, ad_views 호출 관계 및 static 경로 등록 책임 교정 |
| 수정 | `docs/server-routing/files/server/game/ad_views.py.md` | 실제 ORM→gateway 계약·decorator/인증/CSRF 책임을 설명하고 이 파일에 없는 Mongo/HTTP/테스트 호출 설명 제거 |
| 추가 | `docs/server-routing/day24-progress.md` | 현재 구현/검증/미적용 상태, 광고 HTTP와 Player 파일 snapshot의 책임 경계 및 실행 위치 정리 |
| 추가 | 이 인수인계 | 기존 변경과 이번 문서 작업·검증·한계 기록 |
| 추가 | `docs/server-routing/verification/day24-routing-sync/agent-*.json` | 시작/최종 AST 검사, 실제 HTTP 호출 계약, 공식 1교시 재검사, 문서·경로·해시·최종 상태 증거 |

개발 파일 추가·수정·이동·삭제는 없었다. 새 진행/인수인계/검증 문서는 독립 설명·작업 기록이므로 Python source의 짝 문서를 새로 만들 필요가 없다. 기존 export/checker/data/settings/gateway/views 짝 문서는 AST·경로 검증에서 현재 구현과 일치해 재작성하지 않았다. 일반 Spark 문서도 변경하지 않았다.

## 설계 결정과 책임 경계

- `ad_views`는 로그인 User의 Player를 ORM으로 읽고 gateway를 호출한다. 광고 저장소를 직접 호출하거나 광고 서버 인증용 매체 키를 클라이언트에 보내지 않는다. 성공 사건 응답에만 Cache-Control=no-store를 설정한다.
- 게임 `urls.py`는 실제 preview/decision/events와 기존 게임 HTTP callable을 등록한다. static 등록은 이 파일의 책임이 아니다. 기존 중복 인증 경로는 먼저 등록된 auth_views가 선택된다는 구현을 그대로 기록했다.
- `export_player_snapshot`은 `target = Path(options["output"])`을 사용한다. 저장소 루트 실행의 `data/exports/...`가 기존 DATA_DIR와 같은 위치이며 관리 명령이 DATA_DIR를 자동 결합하지 않는다. Python을 경로 보정 목적으로 수정하지 않았다.
- snapshot 원본과 광고 노출·클릭 receipt는 별개 자료다. 파일명 cdc나 공식 단위검사 통과를 MySQL binlog CDC 관찰·광고 후속 인계 완료로 확대 해석하지 않았다.
- 초기 1교시 실패 기록과 23일차 공식 검사기 다운로드 제한은 역사/미완료 검증 상태로 보존했다. 현재 24일차 공식 검사기 통과와 구별했다.
- 부모의 전체 변경문서 링크 검사에서 기존 라우팅 README의 `../handoffs/2026-09-28-day18-canonical.md`, `../handoffs/2026-09-30-day19-through-period07.md` 대상 부재를 확인했다. 기존 역사 설명과 참조 경로를 보존하고 일반 경로 표기·현재 대상 파일 부재로 최소 정정하여 깨진 링크를 제거했다. 다른 문서로 임의 연결하지 않았다.

## 검사 명령과 결과

`routing-doc-auditor` 스킬을 먼저 실행해 AST 구조화 결과를 기준으로 조사 범위를 좁혔다. 최초 UTF-8 미지정 실행은 subprocess의 CP949 해석 오류가 있어 완료 근거로 쓰지 않았고 아래 `-X utf8` 명령으로 재실행했다.

```powershell
Set-Location C:\MLO01-01\Chapter3\Game-server
.\server\.venv\Scripts\python.exe -X utf8 -B C:\Users\이해나\.codex\skills\routing-doc-auditor\scripts\audit_routing.py --repo . --routing-dir docs/server-routing --format json --output docs/server-routing/verification/day24-routing-sync/agent-final-audit.json
.\server\.venv\Scripts\python.exe -X utf8 -B tools/check_day24_logic.py --project server --period 1 --output docs/server-routing/verification/day24-routing-sync/agent-period01-current.json
git diff --check
```

공식 checker 재실행에서는 검사 프로세스의 TEMP/TMP만 `docs/server-routing/verification/day24-routing-sync/agent-temp`로 지정했다. checker는 SQLite `:memory:`와 TemporaryDirectory에서 실행했고 시험 파일을 정리했다. 실제 MySQL·MongoDB 쓰기, 서버 실행·종료, 실제 export, stage·commit은 하지 않았다.

| 검사 | 결과·근거 |
|---|---|
| 시작/최종 표준 auditor | 변경 Python 2개·심벌 22개, 누락/파싱 오류 0, `summary.ok=true`, 종료 0. agent-start-audit.json / agent-final-audit.json |
| 별도 현재 구현 스코프 | gateway·ad_views·urls·views·test_ads·settings·export·checker 8개·심벌 50개, 짝 문서/색인/시그니처 전부 일치. agent-scope-final.json |
| 광고 HTTP 경로·직접 호출 | 13개 URLPattern의 실제 route와 target을 짝 문서에서 확인. ad_views에 없는 Mongo/HTTP/test 계약 제거. agent-contract-start.json / agent-doc-check.json |
| 공식 현재 1교시 검사 | **passed=12 / failed=0**, SQLite 메모리 전용, Mongo 미연결, 학생 source 해시 보존. agent-period01-current.json |
| 현재 snapshot | 56행, 13,275 bytes, 정확한 8필드와 schema/source, `server/data` 없음, SHA-256 `6ea30948a1c6924b186676511207bd2099683ca00cf1b1582cb595e6437375d0` 유지. agent-doc-check.json |
| 현재 안내 local 링크·보호 파일 | 최초 현재 섹션의 새 local 링크 14개 통과. 보충 마감에서는 변경·추가 문서 7개의 전체 local 링크 32개 통과 및 기존 대상 부재 참조 2개 일반 경로 표기 확인. 시작 보호 대상 개발·설정 파일 165개와 환경 파일 1개 bytes 유지, 실제 snapshot 해시 유지. agent-doc-check.json / agent-state-final.json |
| whitespace | `git diff --check` 종료 0. 기존 CRLF 변환 경고는 내용 오류가 아니며 줄바꿈을 별도 정리하지 않음 |

마감 링크 보충 정정과 2교시 문제틀 작성 중 상태 반영은 문서만 변경했다. 이 보충 뒤 문서 링크 검사와 `git diff --check`를 갱신했으며 코드가 바뀌지 않아 공식 코드 검사를 반복하지 않았다.

코드 검증 후 별도 문서 정합화 단계에서 수정한 짝 문서와 색인을 재확인했고, 인수인계 작성 후 local 링크 검사와 최종 Git 상태를 다시 확인했다. 서브에이전트 마감 목록은 `agent-state-final.json`, 전체 보호 대상·환경 해시 마감은 부모 에이전트의 finish-state.json을 따른다.

## 남은 검증과 다음 작업

문서만 수정했으므로 실제 MySQL snapshot 재수집과 전체 게임/Spark 런타임 테스트는 실행하지 않았다. 기존 22·23일차 통과 기록을 이번에 다시 실행했다고 주장하지 않는다. 23일차 공식 3교시 검사기는 여전히 미저장·미실행이며 자체 계약 검사와 구별한다. 이번 정합화 범위 밖의 전체 오래된 Spark 문서 및 외부 환경 링크는 일괄 조사·수정하지 않았다.

현재 24일차 1교시를 다시 확인하려면 Game-server 루트에서 `python tools/check_day24_logic.py --project server --period 1`을 실행한다. 현재 공개 원본이 있으므로 재생성할 필요는 없다. 새 수집은 `python server/manage.py export_player_snapshot --output data/exports/<새-파일명>.ndjson`처럼 별도 파일을 선택한다. 광고 2교시 작업의 입력은 `../Game-server/data/exports/player-cdc.ndjson`이며 후속 함수·관리 명령의 구현과 공식 교시별 검사는 앞으로 진행할 범위다.
