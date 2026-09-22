# start-dev 두 프로필 정리 인수인계

## 요청 목적과 완료 결과

- 목적: 날짜별로 중복된 실행 분기를 제거하고 NiFi 사용 여부만 선택하게 한다.
- 결과: 사용자 실행 프로필을 `without-nifi`와 `with-nifi` 두 개로 통합했다.
- 기본값은 메모리 사용이 작은 `without-nifi`다.
- 두 프로필 모두 Kafka 3노드와 Spark Master·Worker 1개를 연다. `with-nifi`만 Docker Compose NiFi·ZooKeeper를 추가한다.
- 날짜별 `day16`, `day17`, 기존 `all`, 두 번째 Spark Worker 분기를 제거했다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `e24b87e 15day - 6교시`
- staged 변경: 없음.
- 여러 tracked 수정·삭제와 untracked 파일이 작업 시작 전에 존재했다.
- `tools/start-dev.ps1`, `한번에_실행.md`, 짝 라우팅 문서도 작업 시작 전에 변경 상태였다. 기존 Java·Docker·메모리 설정은 보존하고 프로필 선택 흐름만 정리했다.
- 다른 기존 변경은 수정하거나 되돌리지 않았다.

## 이번 작업에서 변경한 파일

- 수정: `tools/start-dev.ps1`
- 수정: `docs/server-routing/files/tools/start-dev.ps1.md`
- 수정: `한번에_실행.md`
- 추가: 이 인수인계 문서

## 설계 결정과 책임 경계

- `Profile`은 사용자가 선택하는 `with-nifi | without-nifi` 두 값만 허용한다.
- `ChildService`는 프로필 실행기가 별도 서비스 창을 만들 때 사용하는 내부 인자다.
- 기본 `without-nifi`는 Docker CLI를 호출하지 않는다.
- `with-nifi`는 Docker 사전 검사를 수행하며, 실패하면 NiFi만 건너뛰고 Kafka·Spark 실행 경로를 유지한다.
- Spark Worker는 현재 장비의 메모리 기준에 맞춰 한 개만 유지한다.

## 라우팅 문서와 색인

- `tools/start-dev.ps1`의 파라미터, 변수 출처, 검사 흐름, 자식 서비스 호출을 짝 라우팅 문서와 일치시켰다.
- 개발 파일 추가·이동·삭제가 없으므로 라우팅 색인은 변경하지 않았다.
- 사용자 실행 안내의 기존 `all`, `day16`, `day17`, `-Service nifi`, Worker 2 명령을 두 프로필 명령으로 교체했다.

## 실행한 검사와 결과

```powershell
# PowerShell Parser 검사
[System.Management.Automation.Language.Parser]::ParseFile(...)
# 결과: start-dev.ps1 syntax: OK

cmd.exe /d /c start-dev.cmd -CheckOnly
# 결과: without-nifi로 Java·Kafka·Spark 경로와 포트 확인, Docker 검사 생략, 종료 코드 0.

cmd.exe /d /c start-dev.cmd -Profile with-nifi -CheckOnly
# 결과: Java·Kafka·Spark·NiFi 경로와 포트 확인. Docker Engine 미실행을 경고로 표시하고 종료 코드 0.
```

- 검사 시 Kafka 3노드와 Spark Master·Worker 포트는 이미 사용 중이었다. 검사 모드는 기존 서비스를 유지했으며 새 프로세스를 시작하지 않았다.

## 실행하지 않은 검사와 남은 위험

- 기존 Kafka·Spark가 실행 중이므로 실제 프로필 실행으로 중복 창을 만들지 않았다.
- Docker Engine이 꺼져 있어 NiFi의 실제 Compose 시작은 수행하지 않았다.
- 작업 시작 전에 존재한 다른 변경과 untracked 파일은 이번 검증 범위에서 제외했다.

## 다음 실행 순서

NiFi가 필요 없을 때:

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\start-dev.cmd
```

NiFi가 필요할 때:

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\start-dev.cmd -Profile with-nifi
```
