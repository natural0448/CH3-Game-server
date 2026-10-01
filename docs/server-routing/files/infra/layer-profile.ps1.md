# infra/layer-profile.ps1

## 책임과 입력·변수

Windows 실행 프로필. 파라미터·함수 없음. Game-server 루트에서 dot-source. $sparkSubmit은 Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1/bin/spark-submit.cmd의 실제 절대경로.

아래 root는 `file:///C:/MLO01-01/Chapter3/Game-server/data/lake`를 뜻한다. 환경변수는 dot-source한 PowerShell 세션이 소유하며 이 파일이 값을 설정한다.

## 직접 호출·의사코드

모듈/스크립트 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다. 파라미터 기본값·허용 범위는 위 입력 항목과 같다. 반환값은 없고 결과는 출력·Parquet·JSON 또는 셸 변수다. 각 중간 변수는 현재 파일이 소유한다.

```text
SPARK_MASTER_URL=spark://127.0.0.1:7077
BRONZE_INPUT_URI=file:///C:/MLO01-01/Chapter3/Game-server/data/lake/bronze/game/capture-002/events.ndjson
PARSED_URI=같은 root/staging/parsed-capture-002
QUALITY_URI=같은 root/staging/quality-capture-002
SILVER_BASE_URI=같은 root/silver/game_actions/capture-002-base
SILVER_URI=같은 root/silver/game_actions/capture-002
GOLD_URI=같은 root/gold/game_daily/capture-002
URI와 Spark 실행 경로만 현재 PowerShell에 설정; 작업 실행·복사·서비스 시작은 하지 않는다
```

직접 호출은 위에 명시한 SparkSession/DataFrame 함수, Python 표준 json/Path/datetime/os 또는 실행 명령이다. Spark API 결과는 다음 단계의 표나 실제 건수이며 네트워크·게임 규칙의 내부 구현을 설명하지 않는다.
