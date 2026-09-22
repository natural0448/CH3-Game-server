import argparse
import json
from pathlib import Path

from pyspark.sql import SparkSession, functions as F


ACTION_TYPES = ("player.moved", "player.gathered", "player.trained")
SHUFFLE_PARTITIONS = 4
EVENT_SCHEMA = """
    schema_version int,
    event_id string,
    event_type string,
    player_id long,
    room_id string,
    event_time string,
    payload struct<
        command_id:string,
        x:int,
        y:int,
        coins:long,
        version:long,
        action_label:string
    >
"""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--bootstrap-servers", required=True)
    parser.add_argument("--topic", default="game.actions.v1")
    parser.add_argument(
        "--kind",
        choices=["tumbling", "sliding"],
        default="tumbling",
    )
    return parser.parse_args()


def read_actions(spark, bootstrap_servers, topic, kind):
    messages = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("subscribe", topic)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "true")
        .option("groupIdPrefix", f"village-game-windows-{kind}")
        .load()
    )
    parsed = messages.select(
        F.col("value").cast("string").alias("raw_value"),
        F.col("topic").alias("kafka_topic"),
        F.col("partition").alias("kafka_partition"),
        F.col("offset").alias("kafka_offset"),
        F.from_json(
            F.col("value").cast("string"), EVENT_SCHEMA
        ).alias("event_data"),
    )
    actions = parsed.select(
        "event_data.*",
        "raw_value",
        "kafka_topic",
        "kafka_partition",
        "kafka_offset",
    ).withColumn("event_time", F.to_timestamp("event_time"))
    return actions.filter(
        F.col("event_time").isNotNull()
        & F.col("event_id").isNotNull()
        & (F.col("schema_version") == 1)
        & F.col("event_type").isin(*ACTION_TYPES)
    )


def build_windows(actions, kind):
    duration = "10 seconds" if kind == "tumbling" else "20 seconds"
    windows = (
        actions.withWatermark("event_time", "10 seconds")
        .groupBy(F.window("event_time", duration, "10 seconds"), "event_type")
        .count()
    )
    return windows.select(
        F.lit(kind).alias("kind"),
        F.col("window.start").alias("window_start"),
        F.col("window.end").alias("window_end"),
        "event_type",
        "count",
    )


def main():
    args = parse_args()
    data_dir = Path(args.data_dir).resolve()
    output = data_dir / "lake" / "windows" / args.kind
    checkpoint = data_dir / "checkpoints" / "windows" / args.kind
    progress_path = data_dir / "marts" / f"progress-windows-{args.kind}.json"
    output.mkdir(parents=True, exist_ok=True)
    checkpoint.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    spark = (
        SparkSession.builder.appName(f"game-windows-{args.kind}")
        .config("spark.sql.session.timeZone", "Asia/Seoul")
        .config("spark.sql.shuffle.partitions", str(SHUFFLE_PARTITIONS))
        .getOrCreate()
    )
    query = None
    try:
        # The window clock is the server event_time, not the aggregation time.
        # raw_value preserves the complete transformed event envelope.
        actions = read_actions(
            spark,
            args.bootstrap_servers,
            args.topic,
            args.kind,
        )
        actions.printSchema()
        print("streaming input:", actions.isStreaming, flush=True)

        final_windows = build_windows(actions, args.kind)
        print("window output:", output, flush=True)
        print("window checkpoint:", checkpoint, flush=True)
        query = (
            final_windows.writeStream.format("parquet")
            .outputMode("append")
            .option("path", output.as_uri())
            .option("checkpointLocation", checkpoint.as_uri())
            .queryName(f"game-windows-{args.kind}")
            .trigger(processingTime="5 seconds")
            .start()
        )
        last_batch_id = None
        while not query.awaitTermination(5):
            snapshot = query.lastProgress
            if snapshot is None:
                continue
            progress_json = snapshot.json if hasattr(snapshot, "json") else None
            if callable(progress_json):
                progress_json = progress_json()
            progress = (
                json.loads(progress_json)
                if progress_json is not None
                else snapshot
            )
            batch_id = progress.get("batchId")
            if batch_id is None or batch_id == last_batch_id:
                continue

            temporary = progress_path.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(progress, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temporary.replace(progress_path)
            last_batch_id = batch_id
            print(
                json.dumps(
                    {
                        "kind": args.kind,
                        "batchId": batch_id,
                        "numInputRows": progress.get("numInputRows"),
                        "eventTime": progress.get("eventTime", {}),
                        "stateOperators": progress.get("stateOperators", []),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    except KeyboardInterrupt:
        print(
            "Stopping window query; output and checkpoint are preserved.",
            flush=True,
        )
    finally:
        if query is not None and query.isActive:
            query.stop()
        spark.stop()


if __name__ == "__main__":
    main()
