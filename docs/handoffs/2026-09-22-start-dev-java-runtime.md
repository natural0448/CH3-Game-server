# start-dev 프로젝트 Java 복구 인수인계

## 요청 목적과 완료 결과

- 목적: 시스템 `java` 명령이 사라진 상태에서도 `start-dev.cmd`가 실행되게 한다.
- 결과: 실행기가 프로젝트에 포함된 Temurin Java 21을 우선 선택하고 현재 실행기 및 자식 서비스 창에만 `JAVA_HOME`과 `PATH`를 전달한다.
- `tools/kafka.ps1`을 직접 호출할 때도 같은 Java 선택 규칙을 적용했다.
- Docker Desktop이 꺼졌거나 실행이 거부된 경우 Docker 사전 검사가 전체 실행을 중단하지 않고 NiFi 문제로 반환되게 했다.
- Docker/NiFi 없이 Kafka 3노드와 Spark Master·Worker 1개만 여는 `day17` 프로필을 추가했다.
- 검사 중 실제 Kafka, Spark, NiFi 서비스는 시작하지 않았다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `e24b87e 15day - 6교시`
- staged 변경: 없음.
- 작업 시작 전에 여러 tracked 수정·삭제와 untracked 파일이 이미 있었다.
- 이번 요청과 겹친 `tools/start-dev.ps1`, `tools/kafka.ps1` 및 두 짝 라우팅 문서도 작업 시작 전에 변경 상태였다. 기존 내용을 보존하고 Java 선택과 `day17` 실행에 필요한 부분만 추가했다.
- 그 밖의 기존 변경은 수정하거나 정리하지 않았다.

## 이번 작업에서 변경한 파일

- 수정: `tools/start-dev.ps1`
  - 프로젝트 Java 21 우선 탐색과 현재 프로세스 환경 설정
  - `day17` 프로필
  - Docker 실행 실패를 사전 검사 결과로 변환
- 수정: `tools/kafka.ps1`
  - 프로젝트 Java 21 우선 탐색
  - Kafka 도구와 노드 실행을 선택된 `java.exe` 절대경로로 호출
- 수정: `docs/server-routing/files/tools/start-dev.ps1.md`
- 수정: `docs/server-routing/files/tools/kafka.ps1.md`
- 추가: 이 인수인계 문서

## 설계 결정과 책임 경계

- Java 선택 우선순위는 프로젝트 번들, 현재 `JAVA_HOME`, 현재 `PATH` 순서다.
- 시스템 또는 사용자 환경 변수는 영구 변경하지 않는다. 새 서비스 터미널은 부모 실행기의 프로세스 환경만 상속한다.
- `day17`은 Kafka와 Spark만 담당한다. Django와 publisher는 시작하지 않는다.
- 기본 `all` 동작은 유지한다. Docker를 사용할 수 없으면 NiFi만 건너뛸 수 있도록 사전 검사 실패를 정상적으로 보고한다.

## 라우팅 문서와 색인

- 두 수정 스크립트의 1:1 라우팅 문서를 실제 시그니처, Java 변수 출처, 선택 순서, 호출 흐름에 맞췄다.
- 개발 파일 추가·이동·삭제가 없으므로 라우팅 색인 항목은 추가하거나 삭제하지 않았다.
- 기존 색인에서 두 스크립트와 짝 문서 연결을 확인했다.

## 실행한 검사와 결과

```powershell
# 두 PowerShell 스크립트 Parser 검사
[System.Management.Automation.Language.Parser]::ParseFile(...)
# 결과: start-dev.ps1 syntax: OK, kafka.ps1 syntax: OK

cmd.exe /d /c start-dev.cmd -Service day17 -CheckOnly
# 결과: 프로젝트 Java 21, Kafka 3노드, Spark Master·Worker 1 파일과 빈 포트 확인. 서비스 시작 없음.

cmd.exe /d /c start-dev.cmd -CheckOnly
# 결과: 프로젝트 Java 21 확인. Docker Engine 미실행을 NiFi 경고로 표시하고 정상 종료.

infra/runtime/temurin-jdk21/jdk-21.0.12.1+1/bin/java.exe -version
# 결과: Temurin OpenJDK 21.0.12.1 LTS, 종료 코드 0.

git diff --check
# 결과: 공백 오류 없음. 기존 파일들의 LF/CRLF 변환 경고만 있음.
```

## 실행하지 않은 검사와 남은 위험

- 사용자가 직접 서비스를 켜겠다고 했으므로 실제 Kafka와 Spark 프로세스는 시작하지 않았다.
- Docker Desktop이 꺼져 있어 NiFi 실제 시작은 검사하지 않았다. Day17 프로필에는 NiFi가 포함되지 않는다.
- 작업 시작 전에 존재한 다른 변경과 untracked 파일은 이번 작업 검증 범위에서 제외했다.

## 다음 실행 순서

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\start-dev.cmd -Service day17 -CheckOnly
.\start-dev.cmd -Service day17
```

두 번째 명령은 Kafka 3개, Spark Master, Spark Worker 1을 각각 별도 터미널 창에서 연다. 각 창의 준비 로그를 확인한 뒤 Django와 publisher는 필요한 교시 순서에 따라 별도 터미널에서 실행한다.
