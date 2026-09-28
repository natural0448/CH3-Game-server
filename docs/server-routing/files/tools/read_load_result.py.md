# `tools/read_load_result.py`

## 책임과 호출 경계

이미 저장된 동시 접속 측정 JSON 한 개를 읽어 대표 지표와 방별 연결·성공 응답 합계를 표준 출력한다. 네트워크·Django·Kafka·Spark에는 연결하지 않고 입력 파일을 수정하지 않는다.

## 함수

### `resolve_project_path(value) -> Path`

- `value`: 명령줄에서 받은 문자열 또는 Path형 경로.

절대경로는 그대로 정규화한다. `data/...` 또는 `../data/...` 형태는 `PROJECT_DIR/data/...`로 맞추고, 다른 상대경로만 현재 작업 디렉터리를 기준으로 해석한다.

### `main() -> None`

```text
도움말이 포함된 위치 인자 path를 읽음
resolve_project_path로 프로젝트 데이터 경로를 정규화
파일 누락·UTF-8 JSON 오류를 argparse 오류로 표시
UTF-8 JSON을 해석
generated_at, 연결·요청·오류·경과·처리율·RTT 필드를 순서대로 출력
같은 report의 by_player 행을 room_id별로 묶음
connected=True인 행만 방별 players 수에 더하고 success_count를 합산
방 ID 오름차순으로 by_room 결과 출력
```

직접 호출:

- `argparse.ArgumentParser`: `path` 위치 인자 처리.
- `Path.read_text`: UTF-8 결과 파일 읽기.
- `json.loads`: JSON object 해석.

## 변수와 값의 출처

- `PROJECT_DIR`: 이 파일의 부모인 `tools`의 부모, 즉 `Game-server` 절대경로.
- `options.path`: 사용자가 전달한 결과 파일 경로.
- `path`: `resolve_project_path`가 반환한 절대경로.
- `report`: 결과 파일 최상위 JSON object.
- `by_room`: `report["by_player"]`에서 만든 방별 연결 플레이어 수와 성공 응답 합계. `main()`의 지역 변수다.
- 출력 키 목록: `ws_load.py`가 저장하는 대표 집계 필드 이름.
