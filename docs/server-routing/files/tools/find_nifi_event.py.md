# `tools/find_nifi_event.py`

## 책임과 호출 경계

NiFi가 저장한 JSON 파일 디렉터리에서 사용자가 지정한 `event_id`와 같은 사건을 찾는다. 지정 디렉터리의 바로 아래 일반 파일만 읽고, Kafka·NiFi API·데이터베이스에는 연결하지 않는다. 파일을 수정하거나 이동하지 않는다.

## 명령행 파라미터

```text
--directory: str, 필수
  검색할 NiFi 출력 디렉터리. Path.resolve()로 절대경로를 만든 뒤 실제 디렉터리인지 검사한다.

--event-id: str, 필수
  찾을 사건 ID. UUID(...)로 유효성을 확인하고 표준 문자열로 바꾼다.

--max-files: int, 기본값 2000, 허용 범위 1..10000
  정렬된 디렉터리 항목 중 검사할 일반 파일의 최대 수다.
```

## 함수

### `main()`

반환값은 없으며 결과 JSON을 표준 출력에 쓴다.

```text
명령행 인자 파싱
event-id를 UUID 표준 문자열로 검증
max-files 범위와 directory 존재 여부 검사

directory.iterdir() 결과를 이름순으로 순회
숨김 파일과 디렉터리는 제외
max-files에 도달하면 scan_truncated=true 후 중단
1MiB보다 큰 파일은 unreadable_or_nonobject_files에 합산
UTF-8 JSON object로 읽지 못한 파일도 같은 오류 수에 합산
event_id가 요청 UUID와 같으면 matching_files 증가
최대 20개까지 filename과 event 원문을 matches에 보관

검색 통계와 matches를 UTF-8 JSON으로 표준 출력
반환값 없음
```

직접 호출하는 외부 코드:

- `argparse.ArgumentParser`: 명령행 파라미터와 오류 출력을 관리한다.
- `uuid.UUID`: 요청 ID가 UUID인지 검증하고 표준 형식으로 정규화한다.
- `pathlib.Path`: 디렉터리 확인, 파일 열거, 크기 확인과 UTF-8 읽기를 수행한다.
- `json.loads` / `json.dumps`: 파일 JSON을 해석하고 결과 JSON을 출력한다.

## 주요 변수와 값의 출처

```text
event_id
  출처: --event-id. UUID 검증을 통과한 표준 문자열.

directory
  출처: --directory. resolve()가 반환한 절대경로.

scanned
  이 함수가 증가시키는 실제 검사 파일 수.

malformed
  1MiB 초과, 읽기 실패, JSON 파싱 실패 또는 object가 아닌 파일 수.

matching_count
  event_id가 일치한 전체 파일 수.

matches
  일치 파일 가운데 처음 20개의 filename·event object 목록.

truncated
  max-files 때문에 디렉터리 순회를 끝냈는지 나타내는 bool.
```

출력의 `scope`는 `bounded-read-of-nifi-output`, `schema_version`은 `1`이다.
