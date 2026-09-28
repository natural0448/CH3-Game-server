# Kafka Windows 보존기간 파일 잠금 복구 인수인계

## 요청 목적과 완료 결과

- 목적: Kafka 노드가 `all log dirs ... have failed`와 함께 반복 종료되는 문제를 해결한다.
- 원인: 7일 보존기간이 지난 세그먼트를 정리하면서 Kafka가 memory-mapped `.index` 파일을 `.deleted`로 바꾸려 했고, Windows가 사용 중인 파일의 rename을 거부했다.
- 기존 `log.cleaner.enable=false`는 compact 작업만 막으며 보존기간에 따른 세그먼트 삭제는 막지 못했다.
- 결과: 세 Kafka 노드에 `log.retention.ms=-1`을 적용해 수업용 Windows 클러스터가 실행 중 세그먼트 삭제·rename을 시도하지 않게 했다.
- 기존 Kafka 데이터, cluster ID, checkpoint, 토픽은 삭제하거나 초기화하지 않았다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-server`
- 직전 커밋: `f94aa6b day16 - complete`
- staged·unstaged·untracked 변경: 없음.
- 마감 확인 시 사용자가 작업 중 추가한 `config/settings.py` 변경과 `server/analytics/management/commands/run_game_delta.py`가 새로 나타났다. 이번 Kafka 수정과 구분했으며 해당 코드는 수정하지 않았다.

## 이번 작업에서 변경한 파일

- 수정: `infra/kafka/node1.properties`
- 수정: `infra/kafka/node2.properties`
- 수정: `infra/kafka/node3.properties`
- 수정: `docs/server-routing/files/infra/kafka/node1.properties.md`
- 수정: `docs/server-routing/files/infra/kafka/node2.properties.md`
- 수정: `docs/server-routing/files/infra/kafka/node3.properties.md`
- 수정: `한번에_실행.md`
- 추가: 이 인수인계 문서
- 사용자 변경 정합화로 추가: `docs/server-routing/files/config/settings.py.md`
- 사용자 변경 정합화로 추가: `docs/server-routing/files/server/analytics/management/commands/run_game_delta.py.md`
- 사용자 변경 정합화로 수정: `docs/server-routing/README.md`

## 중요한 설계 결정과 책임 경계

- 로컬 Windows 수업 환경의 안정성을 위해 broker 기본 시간 보존 삭제를 비활성화했다.
- 복제, ISR, producer·consumer offset, 토픽 데이터 기록은 그대로 유지한다.
- 데이터가 자동 삭제되지 않으므로 디스크 사용량은 계속 증가할 수 있다. 정리는 Kafka 세 노드를 모두 종료한 뒤 별도 백업·초기화 절차로 수행한다.
- 실패가 발생한 `game.events.v1-1`은 오류 전에 log start offset이 이미 35로 진행됐다. 이번 작업은 기존 파일을 삭제하거나 이 offset을 임의로 되돌리지 않았다.

## 라우팅 문서와 색인

- 세 노드 속성 파일의 1:1 라우팅 문서에 `log.retention.ms=-1`의 값, 목적, 디스크 관리 책임을 반영했다.
- 개발 파일 추가·이동·삭제가 없으므로 라우팅 색인은 변경하지 않았다.
- 운영 실행 안내에도 cleaner와 retention의 차이와 오프라인 정리 원칙을 반영했다.
- 작업 중 새로 확인된 사용자 코드 두 파일은 현재 구현 그대로 짝 문서와 색인에 반영했다. `run_game_delta.py`의 클래스 본문에 Spark job 블록이 잘못 들어가 import가 실패하는 현재 상태도 문서에 기록했으며 코드는 교정하지 않았다.

## 실행한 검사와 결과

```powershell
.\tools\kafka.ps1 -Action start -Node 1
.\tools\kafka.ps1 -Action start -Node 2
.\tools\kafka.ps1 -Action start -Node 3
.\tools\kafka.ps1 -Action status
.\tools\kafka.ps1 -Action describe-topic
```

- 세 노드가 기존 데이터로 시작했다.
- KRaft leader가 선출됐고 `MaxFollowerLag: 0`을 확인했다.
- CurrentVoters에 1·2·3번 노드가 모두 포함됐다.
- `game.events.v1`의 세 파티션이 모두 ISR 3개를 회복했다.
- 토픽 설명에서 `retention.ms=-1` 적용을 확인했다.
- 이전 실행에서 약 32초 뒤 발생했던 index rename·log directory 실패가 새 실행에서는 재발하지 않았다.
- 테스트 세션의 `Ctrl+C` 전달이 되지 않아 테스트로 생성한 Kafka Java PID만 강제 종료했다. 이후 Kafka listener가 남지 않은 것을 확인했다. 사용자가 이미 실행 중이던 Spark Master·Worker는 유지했다.

## 실행하지 못한 검사, 남은 위험, 후속 작업

- 실제 7일 경과는 기다리지 않았다. 대신 이미 보존기간을 넘긴 동일 세그먼트가 있는 상태로 재시작해 기존 실패 시점보다 오래 실행했다.
- 자동 retention을 끄므로 `data/kafka` 디스크 크기를 주기적으로 확인해야 한다.
- 장기 운영 환경에서는 Linux Kafka 또는 Kafka가 지원하는 별도 저장 환경과 명시적인 보존 정책을 사용해야 한다. 현재 설정은 로컬 수업 환경용이다.
- 사용자 작성 중인 `run_game_delta.py`는 현재 `data_dir`이 클래스 범위에 없어 import 중 `NameError`가 발생한다. 별도 요청에서 Spark job 쪽으로 잘못 붙은 블록을 이동해야 한다.

## 다음 실행 순서

현재 Spark가 실행 중이면 프로젝트 루트에서 다음 명령만 실행해도 열린 Spark 포트는 유지하고 Kafka 세 창만 추가로 열린다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\start-dev.cmd
```

기동 후 확인:

```powershell
.\tools\kafka.ps1 -Action status
.\tools\kafka.ps1 -Action describe-topic
```
