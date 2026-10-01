# infra/run-game-layers.sh

## 책임과 입력·변수

교안 단계별 Bash 명령 보관. Python/spark-submit은 실행 셸에서 찾는 명령이다. SPARK_MASTER_URL, BRONZE_INPUT_URI, PARSED_URI, QUALITY_URI, SILVER_BASE_URI, SILVER_URI, GOLD_URI는 사용자 설정. capture-002 보존은 기존 run이면 보호 오류로 중단해야 한다.

## 직접 호출·의사코드

모듈/스크립트 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다. 파라미터 기본값·허용 범위는 위 입력 항목과 같다. 반환값은 없고 결과는 출력·Parquet·JSON 또는 셸 변수다. 각 중간 변수는 현재 파일이 소유한다.

```text
capture_game → store_bronze(capture-002)
parse_game_bronze(BRONZE_INPUT_URI → PARSED_URI)
check_game_quality(PARSED_URI → QUALITY_URI)
dedup_game_actions(QUALITY_URI/accepted → SILVER_BASE_URI)
add_game_date(SILVER_BASE_URI → SILVER_URI)
build_game_daily(SILVER_URI → GOLD_URI)
publish_game_summary(SILVER_URI → data/marts/game-summary.json)
write_layer_contract를 spark-submit으로 실행
build_game_daily --event-type player.gathered를 GOLD_URI-gathered에 저장
Windows에서는 이 Bash 파일 대신 인수인계의 PowerShell 명령을 한 줄씩 실행. 앞 단계 실패 시 다음 줄은 실행하지 않는다
```

직접 호출은 위에 명시한 SparkSession/DataFrame 함수, Python 표준 json/Path/datetime/os 또는 실행 명령이다. Spark API 결과는 다음 단계의 표나 실제 건수이며 네트워크·게임 규칙의 내부 구현을 설명하지 않는다.
