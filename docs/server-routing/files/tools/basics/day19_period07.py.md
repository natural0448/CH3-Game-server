# tools/basics/day19_period07.py

## 책임과 호출 계층

독립 Python 연습 파일이다. 행 수와 서로 다른 key 수를 비교하며 서버·Spark를 호출하지 않는다.

## 변수와 직접 호출

- `rows`: `partition=0`, `key="7"`과 `key="8"`인 사전 두 개로 시작한다. 첫 출력 뒤 같은 partition의 `key="7"` 행을 추가해 세 행이 된다.
- `keys`: 빈 set으로 시작하며 반복문이 `row["key"]`를 추가한다.
- `row`: `rows` 반복문의 현재 사전.
- 직접 호출: `print`, `len`, `set`, `keys.add`. 반환값을 외부에 전달하지 않는다.

## 실행 의사코드

```text
두 행을 만든다
첫 행과 len(rows)를 출력한다
각 행의 key를 keys에 넣는다
len(keys)를 출력한다
key="7" 행을 rows에 추가한다
빈 keys를 다시 만들고 rows의 key를 모은다
행 수 3, 서로 다른 key 수 2를 출력한다
```

클래스·함수·메서드 정의 및 CLI 인자는 없다.
