# spark_jobs/publish_game_summary.py

## 책임과 입력·변수

Silver 화면 요약 게시. CLI --input/--output 필수. actions/rooms는 행동·방별 count. dataset_version=Path(args.input.rstrip("/")).name으로 선택한 Silver run 이름. source=silver. schema_version=1, generated_at=현재 UTC ISO, event_count=Silver count, by_action/by_room=count collect 배열.

## 직접 호출·의사코드

모듈/스크립트 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다. 파라미터 기본값·허용 범위는 위 입력 항목과 같다. 반환값은 없고 결과는 출력·Parquet·JSON 또는 셸 변수다. 각 중간 변수는 현재 파일이 소유한다.

```text
Silver 읽기 → rooms.count>100이면 중단
기존 다섯 필드 및 dataset_version/source로 작은 summary 만들기
Path(output).parent.mkdir → UTF-8 .tmp JSON 쓰기 → replace 게시
print → spark.stop
원본 이벤트·계정 정보는 collect하지 않음
```

직접 호출은 위에 명시한 SparkSession/DataFrame 함수, Python 표준 json/Path/datetime/os 또는 실행 명령이다. Spark API 결과는 다음 단계의 표나 실제 건수이며 네트워크·게임 규칙의 내부 구현을 설명하지 않는다.
