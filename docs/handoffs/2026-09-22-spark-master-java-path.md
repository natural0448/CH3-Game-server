# Spark Master Java 경로 복구 인수인계

## 요청 목적과 완료 결과

- 목적: `start-dev.cmd`에서 Spark Master 창이 바로 종료되는 문제를 진단하고 수정한다.
- 원인: 외부 Spark의 `conf/spark-env.cmd`가 실행기에서 선택한 Java 21을 삭제된 JDK 17 경로로 다시 덮어썼다.
- 추가 원인: `TEMP`와 `TMP`가 실제 Spark 설치 폴더가 아닌 `C:/MLO01-01/Chapter3/Spark-exam/spark-tmp`를 가리켰다.
- 결과: 유효한 호출자 `JAVA_HOME`은 유지하고, 없거나 유효하지 않을 때 Game-server의 Temurin Java 21로 대체한다. 임시 폴더는 실제 Spark 설치 폴더 아래에서 계산한다.

## 작업 시작 전 Git 상태

- Game-server 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `e24b87e 15day - 6교시`
- staged 변경: 없음.
- 여러 tracked 수정·삭제와 untracked 파일이 작업 시작 전에 존재했다. 이 작업은 해당 기존 변경을 정리하거나 되돌리지 않았다.
- 수정 대상 외부 Spark 폴더 `C:/MLO01-01/Chapter3/Oder-insight`는 Git 저장소가 아니다. `Git 상태 확인 불가: 저장소 아님`으로 기록한다.
- `spark-env.cmd`와 그 짝 라우팅 문서는 작업 시작 전에 존재했으며, 먼저 현재 설정을 확인한 뒤 수정했다.

## 이번 작업에서 변경한 파일

- 수정: `C:/MLO01-01/Chapter3/Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1/conf/spark-env.cmd`
- 수정: `docs/server-routing/files/external/spark/conf/spark-env.cmd.md`
- 추가: 이 인수인계 문서

## 설계 결정과 책임 경계

- `tools/start-dev.ps1`이 제공한 유효한 `JAVA_HOME`을 Spark 환경 파일이 덮어쓰지 않는다.
- 직접 Spark 배치 파일을 실행해 `JAVA_HOME`이 없거나 삭제된 경로인 경우에만 Game-server의 번들 Java 21을 사용한다.
- 시스템 또는 사용자 환경 변수는 영구 변경하지 않는다.
- `HADOOP_HOME`은 기존처럼 실제 Spark 설치 폴더에서 계산하고, `TEMP`와 `TMP`도 그 아래 `spark-tmp`를 사용한다.

## 라우팅 문서와 색인

- `spark-env.cmd`의 Java 선택 조건과 임시 폴더 출처를 1:1 짝 라우팅 문서에 반영했다.
- 개발 파일 추가·이동·삭제가 없으므로 라우팅 색인은 변경하지 않았다.
- 기존 색인에서 외부 Spark 설정과 짝 문서 연결을 확인했다.

## 실행한 검사와 결과

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\start-dev.ps1 -Service spark-master
```

- 수정 전: `The system cannot find the path specified.`를 출력하고 즉시 종료.
- 수정 후: Spark 4.1.3 Master가 `ALIVE` 상태가 됨.
- 확인 포트: REST 6066, Master RPC 7077, Master UI 8080.
- 사용 Java: Game-server의 Temurin OpenJDK 21.0.12.1.
- 검사용 Master 프로세스는 확인 후 종료했고 Java 프로세스와 위 포트가 남지 않은 것을 확인했다.

```powershell
cmd.exe /d /c start-dev.cmd -Service day17 -CheckOnly
```

- 결과: Java·Kafka·Spark 파일과 포트 검사 정상, 실제 서비스 시작 없음.

## 실행하지 않은 검사와 남은 위험

- 사용자가 실제 서비스를 직접 실행할 예정이므로 Kafka 3노드와 Spark Worker를 함께 장시간 실행하지 않았다.
- 외부 Spark 설치 폴더는 Git 저장소가 아니므로 Git diff로 외부 설정 변경을 비교할 수 없다.
- Python 기본 경로는 기존 설정을 보존했다. Django Spark 제출 명령은 기존처럼 현재 가상환경 Python을 명시한다.

## 다음 실행 순서

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\start-dev.cmd -Service day17 -CheckOnly
.\start-dev.cmd -Service day17
```

Master 창에서 `I have been elected leader! New state: ALIVE`를 확인하고 `http://127.0.0.1:8080`에서 Worker 등록 상태를 확인한다.
