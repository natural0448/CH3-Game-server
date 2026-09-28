# Spark Worker 2 실행기 반영 인수인계

## 요청 목적과 완료 결과

`tools/start-dev.ps1`에 두 번째 Spark Worker를 추가하고, `한번에_실행.md`를 현재 실행 구조 전체와 대조해 다시 정리했다.

- 기본 `without-nifi`는 Kafka 3노드, Spark Master, Worker 1·2를 연다.
- `with-nifi`는 메모리 여유를 위해 Kafka 3노드, Spark Master, Worker 1과 NiFi Compose를 연다.
- Worker 2는 service 7079, Web UI 8082, work 경로 `work/worker-2`, 4코어·768MB로 등록한다.
- 계속 실행되는 `run_game_delta`는 총 executor core를 1로 제한해 한 Worker만 점유한다.
- 이 작업에서는 새 Worker나 다른 서비스를 실제로 시작하지 않았다.

## 작업 시작 전 Git 상태

- 저장소: `C:\MLO01-01\Chapter3\Game-server`
- 직전 커밋: `27f2bc2 day17 - commit`
- staged 변경: 없음
- 작업 시작 전에 존재한 modified 파일:
  - `docs/server-routing/README.md`
  - `docs/server-routing/files/server/analytics/management/commands/summarize_game.py.md`
  - `server/analytics/management/commands/summarize_game.py`
  - `spark_jobs/game_batch.py`
- 작업 시작 전에 존재한 untracked 파일:
  - `docs/handoffs/2026-09-28-delta-batch-summary.md`
  - `docs/server-routing/files/spark_jobs/game_batch.py.md`

위 기존 변경은 보존했다. `docs/server-routing/README.md`는 기존 변경 파일과 겹치며, 이번 작업에서는 `tools/start-dev.ps1` 색인 설명 한 행만 추가로 수정했다.

## 이번 작업의 파일 변경

수정:

- `tools/start-dev.ps1`
- `server/analytics/management/commands/run_game_delta.py`
- `한번에_실행.md`
- `docs/server-routing/files/tools/start-dev.ps1.md`
- `docs/server-routing/files/server/analytics/management/commands/run_game_delta.py.md`
- `docs/server-routing/README.md`의 `tools/start-dev.ps1` 색인 행

추가:

- `docs/handoffs/2026-09-28-second-spark-worker.md`

이동·삭제한 파일은 없다.

## 설계 결정과 책임 경계

- 실행기 프로필이 인프라 구성만 선택한다. Django, publisher, 변환기, Spark 작업과 접속기는 계속 사용자가 별도 터미널에서 실행한다.
- NiFi를 사용하지 않을 때만 Worker 2를 자동 실행해 Docker가 반환한 메모리를 Spark에 배정한다.
- NiFi 프로필은 Worker 1개를 유지해 NiFi·ZooKeeper 6개 컨테이너와의 메모리 경합을 줄인다.
- Worker 번호에서 포트와 work 경로를 계산하므로 Worker 1·2가 같은 실행 분기를 사용한다.
- Delta 스트림은 executor core 1개만 사용한다. 두 번째 Worker는 일회성 `summarize_game --source delta` 같은 다른 애플리케이션이 배치될 수 있도록 남긴다.

## 라우팅 문서 정합화

- `docs/server-routing/files/tools/start-dev.ps1.md`: 프로필별 Worker 수, `spark-worker2`, 포트, 실행 흐름을 실제 코드와 일치시켰다.
- `docs/server-routing/files/server/analytics/management/commands/run_game_delta.py.md`: 총 executor core 1과 자원 경계를 반영했다.
- `docs/server-routing/README.md`: 실행기의 프로필별 Worker 책임을 반영했다.

## 실행한 검사

- PowerShell parser로 `tools/start-dev.ps1` 구문 검사: 통과
- `start-dev.cmd -Profile without-nifi -CheckOnly`: 통과
  - 기존 Kafka 3노드, Spark Master, Worker 1 포트 사용 중 확인
  - Worker 2의 7079·8082 포트가 비어 있음 확인
  - 프로세스 시작 없음
- `start-dev.cmd -ChildService spark-worker2 -CheckOnly`: 통과
- `start-dev.cmd -Profile with-nifi -CheckOnly`: 스크립트 검사 완료
  - Docker Engine이 꺼져 있어 NiFi preflight 경고 발생
  - 프로세스 시작 없음
- `python -m py_compile analytics/management/commands/run_game_delta.py`: 통과
- `python manage.py help run_game_delta`: 통과
- 코드·라우팅 문서의 Worker 2 포트와 executor core 계약 대조: 통과
- `git diff --check`: 통과. Git의 LF→CRLF 안내만 표시됨

## 남은 위험과 후속 확인

- 실제 Worker 2 등록은 서비스를 남겨 두지 않기 위해 이 작업에서 실행하지 않았다.
- 현재 7079·8082 포트는 비어 있다. 다음 기본 실행 때 Worker 2가 새로 열린다.
- NiFi 프로필의 Compose 내용은 Docker Engine이 꺼져 있어 이번 작업에서 완전 검증하지 못했다. NiFi 사용 시 Docker Desktop 준비 후 다시 `-CheckOnly`를 실행한다.
- Spark scheduler가 실행 중 애플리케이션을 어느 Worker에 놓는지는 가용 자원에 따라 결정한다. Master UI에서 Worker별 executor를 확인한다.

## 다음 실행 순서

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\start-dev.cmd -Profile without-nifi -CheckOnly
.\start-dev.cmd -Profile without-nifi
```

Spark Master UI `http://127.0.0.1:8080`에서 Worker 1의 7078과 Worker 2의 7079가 모두 `ALIVE`인지 확인한다. 그 뒤 필요한 Django, publisher, 변환기와 Delta 작업은 `한번에_실행.md` 순서로 별도 터미널에서 실행한다.
