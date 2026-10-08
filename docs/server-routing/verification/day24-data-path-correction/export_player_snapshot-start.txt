import hashlib
import json
import os
import tempfile
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from django.utils import timezone

from game.models import Player

class Command(BaseCommand):
    help = "게임 공개 상태를 player-snapshot/v1 NDJSON으로 내보냅니다."

    def add_arguments(self, parser):
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        target = Path(options["output"])
        target.parent.mkdir(parents=True, exist_ok=True)
        captured_at = timezone.now().isoformat()
        rows = Player.objects.order_by("id").values(
            "id", "room_id", "coins", "version", "updated_at").iterator()
        temporary_path = None
        count = 0
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=target.parent, delete=False) as stream:
                temporary_path = Path(stream.name)
                for player in rows:
                    updated_at = player["updated_at"]
                    if timezone.is_naive(updated_at):
                        raise ValueError("updated_at에 시간대가 없습니다.")
                    row = {"schema_version": "player-snapshot/v1",
                           "source_kind": "player-snapshot", "captured_at": captured_at,
                           **player, "updated_at": updated_at.isoformat()}
                    stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                    count += 1
            checksum = hashlib.sha256(temporary_path.read_bytes()).hexdigest()
            os.replace(temporary_path, target)
        except (OSError, TypeError, ValueError, DatabaseError) as exc:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise CommandError(str(exc)) from exc
        self.stdout.write(json.dumps({"path": str(target), "rows": count, "sha256": checksum,
                                      "schema_version": "player-snapshot/v1",
                                      "source_kind": "player-snapshot",
                                      "captured_at": captured_at if count else None},
                                     ensure_ascii=False, sort_keys=True))