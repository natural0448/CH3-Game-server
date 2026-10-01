# 20일차 8교시까지 필요한 수정

## 결과와 범위

교안 `Bronze·Silver·Gold로 만드는 마을 일별 통계.html`과 현재 구현을 비교했다. 필요한 날짜·버전·계약·명령 연결과 채집 미션만 수정했다. 서버 인증·URL·모델·게임 명령과 폴더 구조는 변경하지 않았다. 기존 Bronze capture-001/002, Silver/Gold capture-001, 게시 중인 data/marts/game-summary.json은 쓰거나 삭제하지 않았다. 신규 게임 행동·Kafka 수집을 실행하지 않았다.

## 작업 시작 전 Git

- Chapter3: Git 상태 확인 불가: 저장소 아님.
- Game-server: HEAD `21f0929 day20 - mission 1~3`. staged·unstaged 없음. untracked는 infra/run-game-layers.sh, output data/, spark_jobs/add_game_date.py, build_game_daily.py, dedup_game_actions.py, publish_game_summary.py, tools/basics/day20_period03.py~08.py, tools/write_layer_contract.py였다.
- Game-client: HEAD `6367374 day20 - mission 3`. staged·unstaged·untracked 없음.
- 위 server 파일은 작업 시작 전에 존재한 사용자 변경이다. baseline SHA-256과 종료 시 파일 hash를 대조하여 아래 수정 파일만 구분했다. Git 초기화·커밋·staging은 하지 않았다.

## 이번 개발 변경

- 수정 spark_jobs/add_game_date.py: 기존 UTC parsed_time과 원문 event_time을 보존하고 한국 event_date만 추가한다. 기존 날짜 경계 예제 세 행은 유지했다.
- 수정 spark_jobs/build_game_daily.py: 선택 인자 --event-type을 추가했다. 기본값 None은 기존 전체 집계이며 player.gathered 미션은 별도 출력에 저장한다. 필터를 선택한 경우 합계 검사도 같은 입력 범위를 사용한다.
- 수정 spark_jobs/publish_game_summary.py: dataset_version을 실행 날짜 대신 선택한 Silver 디렉터리 이름에서 얻는다. source=silver를 추가하여 실제 원천을 표시한다. 기존 다섯 필드·임시 파일 교체는 유지한다.
- 수정 tools/write_layer_contract.py: 기존 summary 참조·중복 silver_rows 키를 제거하고 선택한 QUALITY_URI/quarantine 및 SILVER_URI의 실제 Spark count를 사용한다. Silver run 이름에 맞는 Bronze manifest를 읽고 calendar_timezone=Asia/Seoul로 기록한다. finally에서 Spark 종료, 계약 출력 부모 폴더 생성은 유지·보완한다.
- 수정 infra/run-game-layers.sh: 잘못된 capture_sample/read_game_actions 파일명, Master·입력 변수, accepted 하위 경로, capture-001 고정을 고쳤다. Spark 계약 작성과 별도 채집 Gold 명령을 붙였다. 교안의 Bash 명령 보관 파일이며 Windows 실행 순서는 아래 PowerShell을 사용한다.
- 수정 tools/basics/day20_period07.py: 추가 합계 출력 이름을 total_rows로 맞췄다.
- 수정 tools/basics/day20_period08.py: 기존 채집 출력과 입력을 보존하고 이동 필터·이동 1 출력을 추가했다.
- 추가 infra/layer-profile.ps1: 현재 Windows 경로의 capture-002 URI와 Spark 실행 파일만 설정한다. 서비스나 작업을 실행하지 않는다.
- client 수정은 별도 [인수인계](../../../Game-client/docs/handoffs/2026-10-01-day20-silver-summary.md)에 기록했다.
- 삭제·이동 없음. 원본 수집/보존 도구, 기존 사용자 출력 구분선, 다른 연습 코드와 output data/는 보존했다.

## 라우팅 정합화

추가 개발 전에 요청 범위의 기존 사용자 구현 16개 파일을 현재 상태로 문서화했다. 검증 후 이번 개발 파일 8개의 문서를 최종 구현으로 다시 맞췄다. docs/server-routing/README.md의 20일차 색인과 아래 17개의 짝 문서를 추가했다.

- spark_jobs/parse_game_bronze.py, check_game_quality.py, dedup_game_actions.py, add_game_date.py, build_game_daily.py, publish_game_summary.py
- tools/write_layer_contract.py, tools/basics/day20_period01.py~08.py
- infra/run-game-layers.sh, infra/layer-profile.ps1

각 문서는 docs/server-routing/files/<상대경로>.md다. Spark 작업과 연습은 모듈 최상위 실행으로 사용자 정의 함수·클래스가 없으며 CLI 기본값/범위, 변수 출처, 직접 호출과 의사코드를 기록했다. 추가 계획이나 미구현 계층은 현재 구조로 기록하지 않았다.

## 실행한 검증

- Python AST 구문 검사 및 연습 1~8 실행: 통과. preserved True, total_events 3, JSON 왕복 capture-001, total_rows 4, 이동 1 확인.
- PowerShell profile 구문 검사: 오류 0. Git Bash `bash -n infra/run-game-layers.sh`: exit 0.
- Native Spark 4.1.3의 격리된 local[1], driver 512m, UI 비활성화로 동일 개발 파일을 실행했다. 별도의 가상 검증 입력 8행이며 운영 관찰값이 아니다. 결과는 Bronze 8, accepted 6, quarantine 2, logical 4, Gold 합 4, 채집 전용 Gold 합 1이다.
- payload 키 순서만 다른 전달은 같은 내용으로 중복 제거됨. 같은 event_id의 다른 내용은 variants=2로 중단하고 출력 미생성 확인.
- 기존 accepted의 reason/value 보존, UTC timestamp 보존, 한국 날짜 9/11→9/12 경계 및 UTC 00:00의 한국 날짜 9/11 확인.
- 실제 Spark count로 계약 생성, summary의 source=silver/dataset_version=capture-001/event_count=4 확인.
- 검증 timestamp 비교는 Spark date_format의 UTC 문자열로 확인했다. 첫 검증의 Python naive datetime 비교가 호스트 시간대 영향을 받아 검증식을 수정해 재검사했으며, 소스 동작 수정으로 처리하지 않았다.
- 검증 JSON → 변경하지 않은 Django summary_view(RequestFactory 인증 사용자) → client read_analytics: HTTP 200 및 버전·원천·건수 일치.
- 검증용 SparkContext는 정상 종료했다. Master·Worker·Kafka·Django·publisher를 켜거나 끄지 않았다.
- AST routing-doc-auditor: 이번 20일차 변경 Python 11개는 이슈 0. 종료 점검 중 사용자가 spark_jobs/layout_projection.py와 tools/basics/day21_period01.py를 추가했다. 전체 기본 변경 범위는 13개이며 이 두 파일의 문서·색인 누락 4건으로 ok=False다. 21일차 파일은 이번 요청 밖이므로 읽거나 수정하지 않았다. 보고서는 docs/server-routing/verification/day20/routing-audit.json.
- Spark 검증 결과 docs/server-routing/verification/day20/spark-verification.json. 실제 운영 수치와 섞지 않는다.
- Git diff --check 통과, 최종 staged 없음. 기존 사용자 untracked와 종료 직전 추가된 21일차 두 파일 보존 확인. 해당 파일을 이번 에이전트 변경으로 주장하지 않는다.

## 사용자가 실행할 순서

프로젝트 루트에서 실행한다. Spark Master·Worker, Kafka·publisher·transform_game_actions는 사용자가 기존 실행기로 준비한다. 실행 시점의 활성 Master는 별도 검증하지 않았으며 격리 검사 결과를 standalone 클러스터 운영 완료라고 주장하지 않는다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server
. .\infra\layer-profile.ps1
```

스크립트 실행 정책에 막히면 해당 PowerShell 세션에만 적용한다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
. .\infra\layer-profile.ps1
```

profile은 capture-002를 선택한다. 현재 이미 보존된 capture-002를 분석할 때는 아래 파싱부터 시작한다. 새로운 행동을 새로 수집하려면 기존 capture-002를 덮어쓰지 말고 새 run-id로 capture/store_bronze하고 profile의 URI도 모두 같은 run으로 맞춘다. 게임에서 채집 두 번, 서버 확정 상태와 실제 이벤트 발행은 이번 작업에서 대신 수행하거나 관찰 완료로 기록하지 않았다.

아래 명령을 한 줄씩 실행한다. 실패하면 다음 단계로 진행하지 않는다. 기존 출력이 있으면 그 결과를 사용하거나 해당 단계부터 새 출력 경로를 지정한다.

```powershell
& $sparkSubmit --master $env:SPARK_MASTER_URL spark_jobs/parse_game_bronze.py --input $env:BRONZE_INPUT_URI --output $env:PARSED_URI
& $sparkSubmit --master $env:SPARK_MASTER_URL spark_jobs/check_game_quality.py --input $env:PARSED_URI --output $env:QUALITY_URI
& $sparkSubmit --master $env:SPARK_MASTER_URL spark_jobs/dedup_game_actions.py --input "$env:QUALITY_URI/accepted" --output $env:SILVER_BASE_URI
& $sparkSubmit --master $env:SPARK_MASTER_URL spark_jobs/add_game_date.py --input $env:SILVER_BASE_URI --output $env:SILVER_URI
& $sparkSubmit --master $env:SPARK_MASTER_URL spark_jobs/build_game_daily.py --input $env:SILVER_URI --output $env:GOLD_URI
& $sparkSubmit --master $env:SPARK_MASTER_URL spark_jobs/publish_game_summary.py --input $env:SILVER_URI --output data/marts/game-summary.json
& $sparkSubmit --master $env:SPARK_MASTER_URL tools/write_layer_contract.py
& $sparkSubmit --master $env:SPARK_MASTER_URL spark_jobs/build_game_daily.py --input $env:SILVER_URI --output "${env:GOLD_URI}-gathered" --event-type player.gathered
```

publish_game_summary 성공 후 접속기를 현재 코드로 재시작하고 전체 → 새로 읽기를 한 번 눌러 원천·버전·생성 시각을 확인한다. 계약은 원본·품질·Silver·Gold의 같은 run을 가리켜야 한다. 실제 게임 채집 두 번, Kafka bounded capture, 로그인한 실화면과 운영 관찰 기록은 사용자가 실행한 뒤 기록한다.
