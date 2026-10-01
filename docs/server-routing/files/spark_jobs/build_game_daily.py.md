# spark_jobs/build_game_daily.py

## 책임과 입력·변수

기본·행동별 Gold. CLI --input/--output 필수. --event-type 기본 None; 허용값 player.moved/player.gathered/player.trained. silver는 입력 Parquet 또는 지정한 행동만 filter한 표. daily 그룹=event_date,room_id,event_type; event_count=count(*), active_players=countDistinct(player_id).

## 직접 호출·의사코드

모듈/스크립트 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다. 파라미터 기본값·허용 범위는 위 입력 항목과 같다. 반환값은 없고 결과는 출력·Parquet·JSON 또는 셸 변수다. 각 중간 변수는 현재 파일이 소유한다.

```text
--event-type이 있으면 먼저 입력 filter
groupBy/agg → event_count 내림차순, 그룹 키 순서로 show
event_date partition errorifexists Parquet 저장
선택한 silver.count와 daily.sum(event_count)를 비교하고 다르면 ValueError
stop
기본 실행은 전체 입력이며 채집 미션은 별도 출력 URI를 사용한다
```

직접 호출은 위에 명시한 SparkSession/DataFrame 함수, Python 표준 json/Path/datetime/os 또는 실행 명령이다. Spark API 결과는 다음 단계의 표나 실제 건수이며 네트워크·게임 규칙의 내부 구현을 설명하지 않는다.
