import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "기존 Spark 클러스터에서 게임 전달 레코드의 시간 창을 계산합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--kind",
            choices=["tumbling", "sliding"],
            default="tumbling",
        )
        parser.add_argument("--topic", default="game.actions.v1")
        parser.add_argument("--data-dir", default=str(settings.DATA_DIR))

    def handle(self, *args, **options):
        if not settings.SPARK_MASTER.startswith("spark://"):
            raise CommandError("Use the existing Spark cluster")

        script = settings.PROJECT_DIR / "spark_jobs" / "game_windows.py"
        if not script.is_file():
            raise CommandError(f"Write the Spark window job first: {script}")

        command = [
            settings.SPARK_SUBMIT,
            "--master",
            settings.SPARK_MASTER,
            "--deploy-mode",
            "client",
            "--driver-memory",
            "768m",
            "--executor-memory",
            "768m",
            "--executor-cores",
            "4",
            "--total-executor-cores",
            "4",
            "--packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.3",
            "--exclude-packages",
            "org.slf4j:slf4j-api",
            "--conf",
            f"spark.pyspark.python={sys.executable}",
            "--conf",
            f"spark.pyspark.driver.python={sys.executable}",
            str(script),
            "--data-dir",
            str(Path(options["data_dir"]).resolve()),
            "--bootstrap-servers",
            ",".join(settings.KAFKA_BOOTSTRAP_SERVERS),
            "--topic",
            options["topic"],
            "--kind",
            options["kind"],
        ]
        env = os.environ.copy()
        env["PYSPARK_PYTHON"] = sys.executable
        env["PYSPARK_DRIVER_PYTHON"] = sys.executable
        try:
            subprocess.run(
                command,
                cwd=settings.BASE_DIR,
                env=env,
                check=True,
            )
        except KeyboardInterrupt:
            self.stdout.write(
                "Stop requested; window output and checkpoint are preserved."
            )
        except subprocess.CalledProcessError as exc:
            raise CommandError(
                f"Spark exited with code {exc.returncode}"
            ) from exc
