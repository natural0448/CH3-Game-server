# `tools/basics/day19_period03.py`

## 책임과 호출 경계

3교시 독립 로컬 연습이다. 고정된 UTF-8 NDJSON 한 줄의 bytes 길이와 원본·복사값의 SHA-256 일치 여부를 출력한다. 파일·Kafka·Django는 호출하지 않는다.

## 최상위 처리 의사코드

```text
raw를 고정 bytes 한 줄로 초기화
bytes(raw)를 copied에 대입
len(raw)를 출력
hashlib.sha256(raw)와 hashlib.sha256(copied)의 hexdigest 일치 여부를 출력
len(raw.splitlines())를 rows에 넣고 출력
```

## 변수와 값의 출처

- `raw`: 코드에 고정한 `b'{"event_id":"e1"}\n'`.
- `copied`: `bytes(raw)`의 결과. 새 객체가 생성됨을 보장하지 않는다.
- `hashlib.sha256`: Python 표준 라이브러리의 SHA-256 계산 함수.
- `rows`: `raw.splitlines()`의 길이. 고정 입력에서는 1이며 원본 bytes는 수정하지 않는다.

정의한 함수·클래스와 명령줄 파라미터는 없다.
