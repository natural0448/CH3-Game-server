# NiFi 클러스터 인프라 실행기 반영 인수인계 (대체됨)

> 2026-09-21에 네이티브 NiFi 실행 방식이 Docker Compose 방식으로 대체됐다. 현재 실행 절차는 `2026-09-21-docker-nifi-start-dev.md`를 따른다.

## 요청 목적과 완료 결과

`C:/MLO01-01/nifi-cluster`의 NiFi 2.12.0 세 노드를 기존 Kafka·Spark 인프라 실행기에 추가했다. `start-dev.cmd` 전체 실행 또는 `-Service nifi1|nifi2|nifi3`로 각 노드를 별도 PowerShell 창에서 실행하도록 연결했다. NiFi에는 해당 창에서만 Java 21을 적용하고 `nifi.cmd run`을 사용한다.

프로젝트 전용 Temurin JDK 21을 공식 Adoptium API에서 받고 SHA-256을 검증했다. 사용자 승인 후 ZooKeeper·포트·상태 공급자 설정을 적용했다. 현재 공유 민감 속성 키가 비어 있어 전체 실행 시 NiFi만 안전하게 건너뛴다. Kafka와 Spark의 기존 실행은 유지한다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`.
- 직전 커밋: `e24b87e 15day - 6교시`.
- staged·unstaged·untracked 파일: 없음.
- 상위 `C:/MLO01-01/Chapter3`는 Git 저장소가 아니며 실제 Git 경계는 `Game-server`였다.

## 이번 작업 파일

수정:

- `tools/start-dev.ps1`
- `한번에_실행.md`
- `docs/server-routing/README.md`

추가:

- `tools/configure-nifi-cluster.ps1`
- `docs/server-routing/files/tools/start-dev.ps1.md`
- `docs/server-routing/files/tools/configure-nifi-cluster.ps1.md`
- `docs/handoffs/2026-09-18-nifi-infra-launcher.md`

이동·삭제: 없음.

`C:/MLO01-01/nifi-cluster` 아래 설정은 사용자 승인 후 변경했으며 각 실행 전에 노드별 `conf/codex-backup-<timestamp>`에 원본을 보관했다.

## 설계 결정과 책임 경계

- 기존 `start-dev.cmd` 진입점을 유지했다.
- NiFi 경로는 프로젝트 위치로부터 `C:/MLO01-01/nifi-cluster`를 계산한다.
- NiFi는 Java 21만 허용하고 Kafka·Spark가 사용하는 전역 Java 설정을 변경하지 않는다.
- 전체 실행에서 NiFi 검사 실패는 Kafka·Spark를 막지 않는다.
- 미완성 NiFi 클러스터를 세 개 띄우는 대신 선행 조건을 검사하고 이유를 표시한다.
- 실행기는 NiFi 설정이나 Flow를 자동 변경하지 않는다.

## 확인된 NiFi 선행 문제

- 프로젝트 `infra/runtime/temurin-jdk21`에 Temurin 21.0.12.1을 설치했고 실행기가 자동 탐색한다.
- 세 노드의 상태 공급자 주소, 고유 load-balance 포트와 내장 ZooKeeper ensemble은 적용됐다.
- 첫 실기동에서 클러스터 공통 `nifi.sensitive.props.key`가 비어 있어 NiFi가 시작을 중단했다.
- 검증 기동에서 노드별 자체 서명 keystore/truststore가 생성됐다. 공유 키 적용 후 클러스터 TLS 신뢰가 성립하는지는 다음 기동에서 확인해야 한다.

## 라우팅 문서

- `docs/server-routing/README.md`에 로컬 인프라 실행기 항목을 추가했다.
- `docs/server-routing/files/tools/start-dev.ps1.md`에 파라미터, 변수 출처, 함수 시그니처, 의사코드와 외부 호출을 기록했다.
- `docs/server-routing/files/tools/configure-nifi-cluster.ps1.md`에 설정 백업·변경 범위와 미실행 상태를 기록했다.

## 검사

실행:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\start-dev.ps1 -CheckOnly
```

결과:

- 종료 코드 0.
- Kafka·Spark·NiFi 설치 경로 확인.
- 기존 Kafka/Spark 포트 사용 중 상태 확인.
- NiFi 8443~8445와 11443~11445가 비어 있음 확인.
- 위 Java·ZooKeeper·load-balance 문제를 경고로 정확히 출력.
- JDK 설치 후 재검사에서는 Java 경고가 사라지고 ZooKeeper·load-balance 경고만 남음.
- 새 서비스는 시작하지 않았다.

## 다음 확인 순서

1. 사용자 별도 승인 후 세 노드에 동일한 민감 속성 키를 안전하게 적용한다.
2. `start-dev.cmd -CheckOnly`에서 `NiFi preflight passed`를 확인한다.
3. 세 노드를 임시 기동해 클러스터 연결과 TLS 신뢰를 확인한 뒤 종료한다.
4. 이후 `start-dev.cmd`로 사용자가 직접 실행한다.
