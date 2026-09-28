# `tools/compare_load.py`

## 책임과 호출 경계

이미 저장된 두 동시 접속 측정 JSON을 읽어 입력 조건, 실제 연결 수, 처리량과 RTT를 나란히 출력한다. 파일을 수정하거나 네트워크·Django·Kafka·Spark를 호출하지 않는다.

## 함수

### `display_number(value, digits=3)`

`None`은 `측정값 없음`으로 유지하고 숫자는 지정 자릿수로 반올림한다.

### `percent_change(before, after)`

기준값 또는 비교값이 없거나 기준값이 0이면 `None`을 반환한다. 그 외에는 `(after-before)/before*100`을 반환한다.

### `main()`

```text
left/right JSON 경로 파싱 후 UTF-8 object 읽기
각 파일의 요청 계정 수·연결 성공 수·최고 동시 연결 수를 한 줄로 구분 출력
기간·간격·성공·오류·처리율·p95 출력
두 실행의 interval과 요청 기간이 같은지 출력
처리율과 p95 변화율을 안전하게 계산해 출력
```

## 변수와 값의 출처

- `paths`: 사용자가 전달한 두 결과 JSON 경로.
- `reports`: 두 파일을 인자 순서로 읽은 object 목록.
- `requested`: `profile.clients`, 입력 조건.
- `connected`: `connected_success`, 로그인과 WS 연결을 마친 계정 수.
- `peak`: `connected_peak`, 관찰 중 동시 열린 연결의 최댓값.
