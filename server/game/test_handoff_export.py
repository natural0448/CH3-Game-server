import json
import uuid
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase

from game.models import GameEvent, Player


class ExportGameHandoffTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="handoff-user")
        self.player = Player.objects.create(user=user, room_id="room-handoff")
        self.first_time = datetime(2026, 9, 28, 1, 0, tzinfo=timezone.utc)
        self.first_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
        self.second_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        GameEvent.objects.create(
            event_id=self.first_id,
            event_type="player.moved",
            player=self.player,
            room_id=self.player.room_id,
            event_time=self.first_time,
            payload={"command_id": "move-1", "x": 1, "y": 0, "version": 1},
        )
        GameEvent.objects.create(
            event_id=self.second_id,
            event_type="player.gathered",
            player=self.player,
            room_id=self.player.room_id,
            event_time=self.first_time + timedelta(minutes=1),
            payload={"command_id": "gather-1", "coins": 1, "version": 2},
        )

    def export(self, directory, **options):
        output = Path(directory) / "game-events.jsonl"
        stdout = StringIO()
        call_command(
            "export_game_handoff", output=str(output), stdout=stdout, **options
        )
        rows = [
            json.loads(line)
            for line in output.read_text(encoding="utf-8").splitlines()
            if line
        ]
        return output, rows, stdout.getvalue()

    def test_exports_ordered_json_lines_without_invented_kafka_positions(self):
        with TemporaryDirectory() as directory:
            output, rows, message = self.export(directory)
            self.assertTrue(output.exists())
            self.assertFalse(output.with_suffix(".jsonl.tmp").exists())

        self.assertEqual([row["event_id"] for row in rows], [
            str(self.first_id), str(self.second_id),
        ])
        self.assertEqual(set(rows[0]), {
            "schema_version", "event_id", "event_type", "player_id",
            "room_id", "event_time", "payload",
        })
        self.assertEqual(rows[0]["payload"]["command_id"], "move-1")
        self.assertTrue(rows[0]["event_time"].endswith("+00:00"))
        self.assertNotIn("kafka_partition", rows[0])
        self.assertNotIn("kafka_offset", rows[0])
        self.assertIn("events=2", message)

    def test_since_is_inclusive_until_is_exclusive_and_timezone_is_required(self):
        second_time = self.first_time + timedelta(minutes=1)
        with TemporaryDirectory() as directory:
            _, rows, _ = self.export(
                directory,
                since=second_time.isoformat(),
                until=(second_time + timedelta(minutes=1)).isoformat(),
            )
        self.assertEqual([row["event_id"] for row in rows], [str(self.second_id)])

        with TemporaryDirectory() as directory, self.assertRaises(CommandError):
            self.export(directory, since="2026-09-28T01:00:00")
