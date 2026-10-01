# 20일차 Windows 계층 처리 명령 수정

## 목적과 결과

사용자 요청대로 `infra/run-game-layers.sh`의 Bash 변수·줄 이어쓰기를 제거하고 실제 Native Spark 설치 경로와 프로젝트 경로를 사용하는 한 줄짜리 PowerShell 명령으로 바꿨다. 파일명과 폴더 구조는 유지했다. 코드·인증·게임 규칙·수집 데이터는 수정하지 않았다.

## 작업 시작 전 Git

- Chapter3: Git 상태 확인 불가: 저장소 아님.
- Game-server: HEAD `a209618 day20-finish`.
- `git status --short`, `git diff --name-status`, `git diff --cached --name-status`: 모두 비어 있었다. staged·unstaged·untracked 기존 변경 없음.
- 수정 전에 기존 명령 파일과 짝 문서가 모두 Bash 상태를 설명하는 것을 확인했다.

## 이번 변경 파일

- 수정 `infra/run-game-layers.sh`: 실제 Spark 실행 경로, Master, Windows 상대 입력·출력 경로를 각 호출에 직접 지정했다. `copy_bronze.py --run-id capture-002`를 연결해 파싱 입력을 원본 사본으로 맞췄다. Silver/Gold는 기존 `data/lake` 구조를 사용한다. 기존 계약 작성·채집 미션을 유지했다. 계약 작성기에서 필요한 세 환경변수만 명시적으로 설정한다.
- 수정 `docs/server-routing/files/infra/run-game-layers.sh.md`: 현재 책임·입력·환경변수 출처·직접 호출·의사코드로 정합화했다.
- 수정 `docs/server-routing/README.md`: 해당 파일의 책임을 PowerShell 명령 보관으로 고쳤다.
- 수정 `docs/handoffs/2026-10-01-day20-through-period08.md`: 이전 Bash 설명·검사가 과거 기록임을 명시하고 이번 기록을 연결했다.
- 추가: 본 인수인계. 개발 파일 추가·이동·삭제 없음.

## 검증

- PowerShell `Parser.ParseInput`로 명령 파일 구문 검사: 오류 0.
- 명령 AST로 Spark 호출 8개를 확인했다. 실제 spark-submit.cmd 및 모든 호출 대상 Python 파일이 존재하고 Master가 `spark://127.0.0.1:7077`임을 확인했다.
- 파싱 → 품질 → accepted → base Silver → 날짜 Silver → Gold/summary/채집 Gold의 입력·출력 연결 검사: 통과.
- 현재 `capture-002` Bronze manifest와 복사본 events.ndjson 존재 확인.
- `routing-doc-auditor` 기본 Git 변경 범위 검사: 시작·종료 모두 이슈 0, 종료 `changed_path_count=5`, `ok=true`. 이번 개발 변경은 `.sh`여서 변경 Python 시그니처 검사는 0개이며 `.sh` 문서·색인은 별도 대조했다. 구조화 검사 결과는 도구 출력으로 확인했다.
- `git diff --check`: 통과. Git의 LF→CRLF 안내는 구문 실패가 아니다.
- 실제 수집·복사·Spark 작업은 실행하지 않았다. 실행 중인 서비스와 게시 JSON을 건드리지 않았다. 클러스터의 현재 가동 여부·실제 작업 성공은 이번 구문/경로 검사 범위가 아니다.
- 최종 Git 상태: 수정 4개·추가 1개는 위 목록과 일치하며 모두 이번 작업 변경이다. staged 없음. 커밋·staging은 수행하지 않았다.

## 사용자가 실행할 순서

`infra/run-game-layers.sh`를 열어 PowerShell에서 필요한 명령을 한 줄씩 실행한다. 확장자 `.sh`는 사용자 요청으로 유지했으므로 Bash로 실행하거나 파일 자체를 실행하는 방식은 사용하지 않는다.

1. 활성 가상환경에서 첫 `cd C:\MLO01-01\Chapter3\Game-server` 실행.
2. 현재 이미 존재하는 capture-002를 재사용한다면 첫 수집·보존·복사 세 줄을 건너뛰고 `parse_game_bronze.py` 호출부터 시작.
3. 각 단계가 성공한 뒤 다음 명령 실행. 기존 Parquet 출력이 있으면 결과를 재사용하거나 이후 연결 경로를 함께 새 경로로 바꾼다. 기존 데이터 삭제 명령은 추가하지 않았다.
4. summary 게시 후 접속기의 새로 읽기 버튼으로 조회. 계약 작성은 바로 위 환경변수 세 줄을 실행한 후 수행.

새 수집본을 만들려면 이미 사용한 capture-002를 재사용하지 말고 새 run-id로 전체 연결 경로를 맞춘다. 명령 파일은 자동 중단 기능이 없는 단계별 실행 목록이다.
