# village_lab에서 새 수집본을 capture-002라는 별도 Bronze 버전으로 보존한다.
python tools/capture_game.py --output data/exports/game-kafka-next.ndjson
python tools/store_bronze.py --input data/exports/game-kafka-next.ndjson --run-id capture-002
# 원본을 Worker 공통 경로에 복사하고 아래 모든 URI를 설정한 뒤 순서대로 실행한다.
# JSON 해석 → 품질 검사 → 중복 제거 → 한국 날짜 추가로 Silver를 만든다.
spark-submit --master "$SPARK_MASTER_URL" spark_jobs/parse_game_bronze.py \
  --input "$BRONZE_INPUT_URI" --output "$PARSED_URI"

spark-submit --master "$SPARK_MASTER_URL" spark_jobs/check_game_quality.py \
  --input "$PARSED_URI" --output "$QUALITY_URI"

spark-submit --master "$SPARK_MASTER_URL" spark_jobs/dedup_game_actions.py \
  --input "$QUALITY_URI/accepted" --output "$SILVER_BASE_URI"

spark-submit --master "$SPARK_MASTER_URL" spark_jobs/add_game_date.py \
  --input "$SILVER_BASE_URI" --output "$SILVER_URI"

spark-submit --master "$SPARK_MASTER_URL" spark_jobs/build_game_daily.py \
  --input "$SILVER_URI" --output "$GOLD_URI"

spark-submit --master "$SPARK_MASTER_URL" spark_jobs/publish_game_summary.py \
  --input "$SILVER_URI" --output data/marts/game-summary.json

spark-submit --master "$SPARK_MASTER_URL" tools/write_layer_contract.py
spark-submit --master "$SPARK_MASTER_URL" spark_jobs/build_game_daily.py \
  --input "$SILVER_URI" --output "${GOLD_URI}-gathered" --event-type player.gathered
