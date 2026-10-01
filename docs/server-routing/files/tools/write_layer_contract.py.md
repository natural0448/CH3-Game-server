# tools/write_layer_contract.py

## 책임과 입력·변수

실제 계층 계약 작성. CLI 인자 없음. 환경변수 SILVER_URI, QUALITY_URI, GOLD_URI 필수. dataset_version=선택한 SILVER_URI의 마지막 경로명. bronze=프로젝트 data/lake/bronze/game/<dataset_version>/manifest.json의 JSON.

## 직접 호출·의사코드

모듈/스크립트 최상위 실행이며 사용자 정의 클래스·함수·메서드는 없다. 파라미터 기본값·허용 범위는 위 입력 항목과 같다. 반환값은 없고 결과는 출력·Parquet·JSON 또는 셸 변수다. 각 중간 변수는 현재 파일이 소유한다.

```text
SparkSession 생성
try: QUALITY_URI/quarantine Parquet count → quarantine_rows; SILVER_URI Parquet count → silver_rows
finally: spark.stop
contract=manifest sha256/rows, 실제 Silver/quarantine count, 환경변수 URI, 현재 UTC created_at
rules=schema_version 1, dedup_key event_id, calendar_timezone Asia/Seoul, gold_grain(event_date,room_id,event_type)
out=data/contracts/layer-contract.json; 부모 폴더 생성 → UTF-8 JSON 쓰기 → print
기존 marts summary에 없는 quarantine_count나 다른 원천 event_count를 읽지 않는다
```

직접 호출은 위에 명시한 SparkSession/DataFrame 함수, Python 표준 json/Path/datetime/os 또는 실행 명령이다. Spark API 결과는 다음 단계의 표나 실제 건수이며 네트워크·게임 규칙의 내부 구현을 설명하지 않는다.
