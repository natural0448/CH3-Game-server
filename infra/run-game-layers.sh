# 파일명은 유지한다. 아래는 Bash가 아닌 PowerShell에서 한 줄씩 실행할 명령이다.
cd C:\MLO01-01\Chapter3\Game-server

# 가상환경이 켜진 상태에서 실행한다. capture-002 원본과 사본이 이미 있으면 아래 세 줄은 건너뛴다.
python tools\capture_game.py --output "data\exports\game-kafka-next.ndjson"
python tools\store_bronze.py --input "data\exports\game-kafka-next.ndjson" --run-id "capture-002"
python tools\copy_bronze.py --run-id "capture-002"

# JSON 해석 → 품질 검사 → 중복 제거 → 한국 날짜 추가. 실패하면 다음 단계는 실행하지 않는다.
# 이미 있는 Parquet 출력은 기존 결과를 사용하거나 새 출력 경로를 지정한다.
& "C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd" --master "spark://127.0.0.1:7077" spark_jobs\parse_game_bronze.py --input "data\copies\bronze\game\capture-002\events.ndjson" --output "data\lake\staging\parsed-capture-002"
& "C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd" --master "spark://127.0.0.1:7077" spark_jobs\check_game_quality.py --input "data\lake\staging\parsed-capture-002" --output "data\lake\staging\quality-capture-002"
& "C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd" --master "spark://127.0.0.1:7077" spark_jobs\dedup_game_actions.py --input "data\lake\staging\quality-capture-002\accepted" --output "data\lake\silver\game_actions\capture-002-base"
& "C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd" --master "spark://127.0.0.1:7077" spark_jobs\add_game_date.py --input "data\lake\silver\game_actions\capture-002-base" --output "data\lake\silver\game_actions\capture-002"

# 같은 Silver에서 일별 Gold와 화면용 집계를 만든다.
& "C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd" --master "spark://127.0.0.1:7077" spark_jobs\build_game_daily.py --input "data\lake\silver\game_actions\capture-002" --output "data\lake\gold\game_daily\capture-002"
& "C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd" --master "spark://127.0.0.1:7077" spark_jobs\publish_game_summary.py --input "data\lake\silver\game_actions\capture-002" --output "data\marts\game-summary.json"

# 계약 작성기가 읽는 세 환경변수만 설정한다. 위 Spark 명령은 변수 설정 없이 실행한다.
$env:QUALITY_URI = "file:///C:/MLO01-01/Chapter3/Game-server/data/lake/staging/quality-capture-002"
$env:SILVER_URI = "file:///C:/MLO01-01/Chapter3/Game-server/data/lake/silver/game_actions/capture-002"
$env:GOLD_URI = "file:///C:/MLO01-01/Chapter3/Game-server/data/lake/gold/game_daily/capture-002"
& "C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd" --master "spark://127.0.0.1:7077" tools\write_layer_contract.py

# 8교시 채집 미션은 전체 Gold와 다른 경로에 저장한다.
& "C:\MLO01-01\Chapter3\Oder-insight\Spark-exam\spark-4.1.3-bin-hadoop3-1\bin\spark-submit.cmd" --master "spark://127.0.0.1:7077" spark_jobs\build_game_daily.py --input "data\lake\silver\game_actions\capture-002" --output "data\lake\gold\game_daily\capture-002-gathered" --event-type "player.gathered"
