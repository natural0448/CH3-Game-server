# tools/basics/day20_period07.py

## 책임과 입력·변수

입력 행 보존 연습. contract=input_version capture-001, accepted_rows 3, quarantine_rows 1. total_rows=두 행 수의 합 4.

## 직접 호출·의사코드

모듈/스크립트 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다. 파라미터 기본값·허용 범위는 위 입력 항목과 같다. 반환값은 없고 결과는 출력·Parquet·JSON 또는 셸 변수다. 각 중간 변수는 현재 파일이 소유한다.

```text
기존 입력 버전·총 행 출력 유지 → total_rows에 합을 저장 → print("total_rows", total_rows)
```

직접 호출은 위에 명시한 SparkSession/DataFrame 함수, Python 표준 json/Path/datetime/os 또는 실행 명령이다. Spark API 결과는 다음 단계의 표나 실제 건수이며 네트워크·게임 규칙의 내부 구현을 설명하지 않는다.
