# tools/basics/day20_period02.py

## 책임과 입력·변수

20일차 2교시 연습. 입력과 중간 변수는 이 파일의 고정 연습값이며 실제 게임 데이터를 읽거나 쓰지 않는다.

## 호출·의사코드

모듈 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다.

```text
rows 두 행을 event_id 기준 accepted/held에 append. len(rows)==len(accepted)+len(held)의 preserved 출력.
```

직접 호출은 위 흐름에 명시한 Python 표준 라이브러리와 Spark API이며 하위 계층 내부는 설명하지 않는다. 반환값은 없고 출력·게시 파일 또는 표가 결과다.
