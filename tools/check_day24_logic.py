"""저장한 학생 코드를 격리 실행한다. 정답 코드를 주입하거나 파일을 고치지 않는다.

예: python check_day24_logic.py --project . --period 2
1교시는 game_server 루트, 2~8교시는 ad_server 루트를 지정한다.
Django는 이 프로세스에서 직접 설정하며 SQLite :memory:만 사용한다.
프로젝트 settings/.env를 읽지 않으며 Mongo 연결은 금지한다.
"""
import argparse
import copy
import hashlib
import importlib
import io
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


FIELDS = {"schema_version", "source_kind", "captured_at", "id", "room_id", "coins", "version", "updated_at"}
PUBLIC = ["id", "room_id", "coins", "version", "updated_at"]
CAUGHT = (ValueError, TypeError, KeyError, OSError)


def row(player_id=1, **updates):
    value = {"schema_version": "player-snapshot/v1", "source_kind": "player-snapshot",
             "captured_at": "2026-10-08T01:00:00+00:00", "id": player_id, "room_id": "room-01",
             "coins": 30, "version": 1, "updated_at": "2026-10-08T00:00:00+00:00"}
    value.update(updates)
    return value


def public(value):
    return {field: value[field] for field in PUBLIC}


def write_rows(path, values):
    path.write_text("".join(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n"
                            for value in values), encoding="utf-8")
    return path


def equal(actual, expected):
    if actual != expected:
        raise AssertionError(f"기대값 {expected!r}; 실제값 {actual!r}")


def rejected(call, exceptions=CAUGHT):
    try:
        call()
    except exceptions:
        return
    raise AssertionError("거절해야 하는 입력을 받아들였습니다.")


class Checks:
    def __init__(self):
        self.results = []

    def run(self, name, call):
        try:
            call()
        except Exception as exc:
            self.results.append({"name": name, "passed": False,
                                 "error": f"{type(exc).__name__}: {exc}"})
        else:
            self.results.append({"name": name, "passed": True})

    def mutation(self, name, call):
        """같은 기대값 검사가 대표 오답을 실제로 잡는지 확인한다."""
        def check():
            rejected(call, (AssertionError,))
        self.run("오답 감지: " + name, check)


def command(module_name, **options):
    from django.core.management import call_command
    stream = io.StringIO()
    command_class = importlib.import_module(module_name).Command
    call_command(command_class(), stdout=stream, **options)
    return json.loads(stream.getvalue())


def test_one(checks, root):
    from django.contrib.auth import get_user_model
    from django.core.management.base import CommandError
    from django.db import connection
    from game.models import Player

    with connection.schema_editor() as editor:
        editor.create_model(get_user_model())
        editor.create_model(Player)
    module_name = "game.management.commands.export_player_snapshot"
    module = importlib.import_module(module_name)
    target = root / "players.ndjson"
    checks.run("빈 실제 QuerySet은 0행 파일", lambda: equal(command(module_name, output=str(target))["rows"], 0))
    checks.run("빈 파일 바이트", lambda: equal(target.read_bytes(), b""))
    user_model = get_user_model()
    for index in (2, 1):
        user = user_model.objects.create(username=f"fixture-{index}")
        Player.objects.create(id=index, user=user, room_id="room-한글", coins=index * 30, version=index)
    result = command(module_name, output=str(target))
    values = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()]
    checks.run("실제 Player ORM id 오름차순", lambda: equal([item["id"] for item in values], [1, 2]))
    checks.run("계정·좌표 제외한 정확한 8필드", lambda: equal([set(item) for item in values], [FIELDS, FIELDS]))
    checks.run("공개 코인·버전", lambda: equal([(item["coins"], item["version"]) for item in values], [(30, 1), (60, 2)]))
    checks.run("captured_at 하나", lambda: equal(len({item["captured_at"] for item in values}), 1))
    checks.run("시각 시간대", lambda: equal(all(datetime.fromisoformat(item["updated_at"]).utcoffset() is not None
                                                  and datetime.fromisoformat(item["captured_at"]).utcoffset() is not None
                                                  for item in values), True))
    checks.run("실제 bytes 체크섬", lambda: equal(result["sha256"], hashlib.sha256(target.read_bytes()).hexdigest()))
    checks.run("반환 행 수", lambda: equal(result["rows"], 2))

    def naive_reject():
        sentinel = b"previous-file\n"
        target.write_bytes(sentinel)
        invalid = {"id": 1, "room_id": "room-01", "coins": 30, "version": 1,
                   "updated_at": datetime(2026, 10, 8)}
        from unittest.mock import MagicMock
        fake = MagicMock()
        fake.objects.order_by.return_value.values.return_value.iterator.return_value = iter([invalid])
        with patch.object(module, "Player", fake):
            rejected(lambda: command(module_name, output=str(target)), (CommandError,))
        equal(target.read_bytes(), sentinel)
        equal(sorted(p.name for p in root.iterdir()), [target.name])
    checks.run("naive 시각 실패는 기존 파일 보존·임시 파일 정리", naive_reject)
    checks.mutation("계정 필드 유출", lambda: equal([set({**item, "user_id": 1}) for item in values], [FIELDS, FIELDS]))


def test_two(checks, module, root):
    source = root / "players.ndjson"
    write_rows(source, [row(2), row(1, coins=-3)])
    expected = {"rows": 2, "public_ids": [1, 2], "source_kind": "player-snapshot",
                "schema_version": "player-snapshot/v1", "captured_at": row()["captured_at"],
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    checks.run("스키마·정렬 ID·음수 코인·실제 체크섬", lambda: equal(module.inspect_snapshot(source), expected))
    empty = write_rows(root / "empty.ndjson", [])
    checks.run("빈 파일 정상", lambda: equal(module.inspect_snapshot(empty), {**expected, "rows": 0, "public_ids": [],
                  "captured_at": None, "sha256": hashlib.sha256(b"").hexdigest()}))
    invalid_rows = [
        ("중복 ID", [row(), row()]), ("bool ID", [row(True)]), ("0 ID", [row(0)]),
        ("bool 코인", [row(coins=True)]), ("소수 코인", [row(coins=1.5)]),
        ("음수 버전", [row(version=-1)]), ("bool 버전", [row(version=False)]),
        ("문자열 아닌 방", [row(room_id=2)]), ("naive updated_at", [row(updated_at="2026-10-08T00:00:00")]),
        ("naive captured_at", [row(captured_at="2026-10-08T01:00:00")]),
        ("captured_at 서로 다름", [row(1), row(2, captured_at="2026-10-08T02:00:00+00:00")]),
        ("광고 스키마 혼입", [row(schema_version="ad-event/v1")]),
        ("fixture 출처 혼입", [row(source_kind="teaching-fixture")]),
        ("계정 필드 추가", [{**row(), "user_id": 1}]),
        ("필수 필드 누락", [{key: value for key, value in row().items() if key != "coins"}]),
        ("사전 아닌 행", [1]),
    ]
    for index, (name, values) in enumerate(invalid_rows):
        invalid = write_rows(root / f"invalid-{index}.ndjson", values)
        checks.run(name + " 거절", lambda invalid=invalid: rejected(lambda: module.inspect_snapshot(invalid)))
    blank = root / "blank.ndjson"
    blank.write_text("\n", encoding="utf-8")
    checks.run("빈 행 거절", lambda: rejected(lambda: module.inspect_snapshot(blank)))
    checks.run("검사 관리명령", lambda: equal(command("ads.management.commands.inspect_player_snapshot", source=str(source)), expected))
    checks.mutation("중복 ID를 사전으로 조용히 덮음", lambda: rejected(lambda: {item["id"]: item for item in [row(), row()]}))


def test_three(checks, module, root):
    result = module.readiness()
    checks.run("입력하지 않은 세 경로", lambda: equal(result["paths"], {name: {"supplied": False, "exists": False}
               for name in ("mysql_config", "connect_home", "debezium_dir")}))
    checks.run("기본 스키마·공통 입력", lambda: equal((result["schema_version"], result["common_input"]),
               ("cdc-readiness/v1", "player-snapshot/v1")))
    exists = root / "my.cnf"
    exists.write_text("# fixture only\n", encoding="utf-8")
    missing = root / "no-connect"
    configured_paths = module.readiness(str(exists), str(missing), str(root))
    checks.run("공급과 존재 구분", lambda: equal(configured_paths["paths"], {
        "mysql_config": {"supplied": True, "exists": True},
        "connect_home": {"supplied": True, "exists": False},
        "debezium_dir": {"supplied": True, "exists": True}}))
    def status(value):
        equal(value["mysql_binlog"], "not-verified")
        for name in ("cdc_reader", "connect_worker", "debezium_connector", "player_change_topic"):
            equal(value[name], "not-configured")
        equal(value["binlog_cdc_observed"], False)
    checks.run("경로가 있어도 CDC 미검증·미구성", lambda: status(configured_paths))
    output = root / "readiness.json"
    checks.run("관리명령 저장", lambda: equal(command("ads.management.commands.write_cdc_readiness",
               output=str(output), mysql_config=str(exists)), json.loads(output.read_text(encoding="utf-8"))))
    checks.mutation("경로 존재를 관찰 성공으로 바꿈", lambda: status({**configured_paths, "binlog_cdc_observed": True}))
    from django.core.management.base import CommandError
    checks.run("폴더를 출력 파일로 지정하면 거절", lambda: rejected(lambda: command(
               "ads.management.commands.write_cdc_readiness", output=str(root)), (CommandError,)))


def test_four(checks, module, root):
    original, updated = public(row(coins=0, version=0)), public(row(coins=30, version=1))
    events = [{"source_kind": "teaching-fixture", "op": "r", "before": None, "after": original},
              {"source_kind": "teaching-fixture", "op": "u", "before": original, "after": updated},
              {"source_kind": "teaching-fixture", "op": "d", "before": updated, "after": None}]
    before_call = copy.deepcopy(events)
    expected = [{"op": "r", "player_id": 1, "coins": 0, "version": 0, "deleted": False},
                {"op": "u", "player_id": 1, "coins": 30, "version": 1, "deleted": False},
                {"op": "d", "player_id": 1, "coins": 30, "version": 1, "deleted": True}]
    checks.run("r/u/d 해석", lambda: equal([module.change_player(event) for event in events], expected))
    checks.run("입력 사건 보존", lambda: equal(events, before_call))
    for name, event in [
        ("실제 CDC라고 가장한 출처", {**events[0], "source_kind": "mysql-binlog"}),
        ("허용하지 않은 op", {**events[0], "op": "c"}),
        ("r before", {**events[0], "before": original}),
        ("u 다른 ID", {**events[1], "after": {**updated, "id": 2}}),
        ("u after 없음", {**events[1], "after": None}),
        ("d after 존재", {**events[2], "after": updated}),
        ("d before 없음", {**events[2], "before": None}),
        ("bool 코인", {**events[0], "after": {**original, "coins": False}}),
        ("naive 시각", {**events[0], "after": {**original, "updated_at": "2026-10-08T00:00:00"}}),
        ("계정 상태 혼입", {**events[0], "after": {**original, "user_id": 1}}),
    ]:
        checks.run(name + " 거절", lambda event=event: rejected(lambda: module.change_player(event)))
    output, summary = root / "changes.ndjson", root / "summary.json"
    result = command("ads.management.commands.write_player_change_fixture", output=str(output), summary=str(summary))
    checks.run("fixture 원문과 해석 결과 분리", lambda: equal((len(output.read_text().splitlines()),
               result["source_kind"], len(result["interpreted"])), (3, "teaching-fixture", 3)))
    checks.run("summary 실제 파일", lambda: equal(json.loads(summary.read_text()), result))
    from django.core.management.base import CommandError
    checks.run("summary로 fixture 원문 덮기 거절", lambda: rejected(lambda: command(
               "ads.management.commands.write_player_change_fixture", output=str(output), summary=str(output)), (CommandError,)))
    checks.mutation("d를 삭제아님으로 반환", lambda: equal({**expected[2], "deleted": False}, expected[2]))


def test_five(checks, module, root):
    source = write_rows(root / "players.ndjson", [row(2), row(1)])
    contract = module.build_snapshot_contract(source)
    inspected = module.inspect_snapshot(source)
    checks.run("실제 검사 결과 그대로", lambda: equal({key: contract[key] for key in inspected}, inspected))
    checks.run("안정 artifact와 v2", lambda: equal((contract["artifact_id"], contract["artifact_version"]),
               ("data/exports/player-cdc.ndjson", "v2")))
    checks.run("실제 source와 collector", lambda: equal((contract["source_path"], contract["collector"]),
               (str(source), "game.export_player_snapshot")))
    checks.run("공개 필드", lambda: equal(contract["public_fields"], PUBLIC))
    checks.run("파일 위치와 Kafka 없음", lambda: equal((contract["position_kind"], contract["kafka_position"],
               contract["binlog_cdc_status"]), ("file-line", None, "not-configured")))
    checks.run("생성 시각 UTC aware", lambda: equal(datetime.fromisoformat(contract["created_at"]).utcoffset().total_seconds(), 0))
    invalid = write_rows(root / "invalid.ndjson", [row(), row()])
    checks.run("중복 입력 계약 거절", lambda: rejected(lambda: module.build_snapshot_contract(invalid)))
    empty = write_rows(root / "empty.ndjson", [])
    checks.run("빈 파일 계약", lambda: equal(module.build_snapshot_contract(empty)["captured_at"], None))
    target = root / "contract.json"
    result = command("ads.management.commands.write_snapshot_contract", source=str(source), output=str(target))
    checks.run("관리명령 실제 저장", lambda: equal(json.loads(target.read_text()), result))
    from django.core.management.base import CommandError
    old_bytes = source.read_bytes()
    checks.run("계약이 원본을 덮는 경로 거절", lambda: rejected(lambda: command(
               "ads.management.commands.write_snapshot_contract", source=str(source), output=str(source)), (CommandError,)))
    checks.run("원본 bytes 보존", lambda: equal(source.read_bytes(), old_bytes))
    checks.mutation("고정 가짜 체크섬", lambda: equal({**inspected, "sha256": "0" * 64}, inspected))


def test_six(checks, module, root):
    before_rows = [row(1), row(2), row(4)]
    after_rows = [row(1, coins=60, version=2), row(3), row(4, captured_at="2026-10-08T02:00:00+00:00")]
    before = {value["id"]: value for value in before_rows}
    after = {value["id"]: value for value in after_rows}
    expected = {"changed": [{"id": 1, "before_version": 1, "after_version": 2,
                             "before_coins": 30, "after_coins": 60}],
                "newly_seen": [3], "missing_unknown": [2]}
    checks.run("변경·새 등장·누락 구분", lambda: equal(module.compare(before, after), expected))
    checks.run("입력 사전 보존", lambda: equal((list(before.values()), list(after.values())), (before_rows, after_rows)))
    checks.run("빈 양쪽", lambda: equal(module.compare({}, {}), {"changed": [], "newly_seen": [], "missing_unknown": []}))
    checks.run("captured_at만 달라짐", lambda: equal(module.compare({1: row()}, {1: row(captured_at="2026-10-09T00:00:00+00:00")})["changed"], []))
    checks.run("같은 순간 다른 offset", lambda: equal(module.compare({1: row()}, {1: row(updated_at="2026-10-08T09:00:00+09:00")})["changed"], []))
    for field, value in [("room_id", "room-02"), ("version", 2), ("updated_at", "2026-10-08T00:01:00+00:00")]:
        checks.run(field + " 변경", lambda field=field, value=value: equal(
                   len(module.compare({1: row()}, {1: row(**{field: value})})["changed"]), 1))
    invalid = write_rows(root / "duplicate.ndjson", [row(), row()])
    checks.run("load_rows 중복을 덮지 않음", lambda: rejected(lambda: module.load_rows(invalid)))
    naive = write_rows(root / "naive.ndjson", [row(updated_at="2026-10-08T00:00:00")])
    checks.run("load_rows naive 시각 거절", lambda: rejected(lambda: module.load_rows(naive)))
    before_path = write_rows(root / "before.ndjson", before_rows)
    after_path = write_rows(root / "after.ndjson", [{**value, "captured_at": "2026-10-08T02:00:00+00:00"} for value in after_rows])
    output = root / "comparison.json"
    checks.run("관리명령 실제 IO", lambda: equal(command("ads.management.commands.compare_player_snapshots",
               before=str(before_path), after=str(after_path), output=str(output)), expected))
    checks.run("비교 결과 파일", lambda: equal(json.loads(output.read_text()), expected))
    from django.core.management.base import CommandError
    checks.run("출력으로 원본 덮기 거절", lambda: rejected(lambda: command(
               "ads.management.commands.compare_player_snapshots", before=str(before_path), after=str(after_path),
               output=str(before_path)), (CommandError,)))
    checks.mutation("누락을 신규로 뒤바꿈", lambda: equal({**expected, "newly_seen": [2]}, expected))


def test_seven(checks, module, root):
    expected = {"missing_unknown": [1, 3], "source_kind": "snapshot-comparison",
                "delete_events": [], "delete_inference_allowed": False}
    before, after = {3: row(3), 1: row(1), 2: row(2)}, {2: row(2), 4: row(4)}
    checks.run("누락 ID 정렬", lambda: equal(module.missing_summary(before, after), expected))
    checks.run("누락 0건", lambda: equal(module.missing_summary(before, before), {**expected, "missing_unknown": []}))
    checks.run("빈 입력", lambda: equal(module.missing_summary({}, {}), {**expected, "missing_unknown": []}))
    checks.run("새 등장 ID는 누락 아님", lambda: equal(module.missing_summary({}, after)["missing_unknown"], []))
    before_path = write_rows(root / "before.ndjson", list(before.values()))
    after_path = write_rows(root / "after.ndjson", list(after.values()))
    output = root / "missing.json"
    checks.run("누락 관리명령", lambda: equal(command("ads.management.commands.read_snapshot_missing",
               before=str(before_path), after=str(after_path), output=str(output)), expected))
    checks.run("실제 기록 파일", lambda: equal(json.loads(output.read_text()), expected))
    bad = write_rows(root / "bad.ndjson", [row(), row()])
    from django.core.management.base import CommandError
    checks.run("잘못된 스냅샷 거절", lambda: rejected(lambda: command("ads.management.commands.read_snapshot_missing",
               before=str(bad), after=str(after_path), output=str(output)), (CommandError,)))
    checks.run("원본 출력 경로 거절", lambda: rejected(lambda: command("ads.management.commands.read_snapshot_missing",
               before=str(before_path), after=str(after_path), output=str(before_path)), (CommandError,)))
    checks.mutation("누락을 삭제 사건으로 생성", lambda: equal({**expected, "delete_events": [{"id": 1, "op": "d"}]}, expected))


def test_eight(checks, module, root):
    source = write_rows(root / "source.ndjson", [row(1), row(2)])
    contract = module.build_snapshot_contract(source)
    contract_path = root / "source-contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    originals = source.read_bytes(), contract_path.read_bytes()
    target = root / "received"
    result = module.handoff_snapshot(source, contract_path, target)
    received = target / "player-cdc.ndjson"
    received_contract = json.loads((target / "player-cdc-contract.json").read_text())
    checks.run("원본 bytes 그대로 전달", lambda: equal(received.read_bytes(), originals[0]))
    checks.run("원본·계약 보존", lambda: equal((source.read_bytes(), contract_path.read_bytes()), originals))
    checks.run("수신 파일 실제 체크섬", lambda: equal(result["sha256"], hashlib.sha256(received.read_bytes()).hexdigest()))
    checks.run("source_path만 수신 경로로 변경", lambda: equal(received_contract,
               {**contract, "source_path": str(received)}))
    checks.run("행·출처·target 반환", lambda: equal((result["rows"], result["source_kind"], result["target"]),
               (2, "player-snapshot", str(target))))
    checks.run("기존 폴더 거절", lambda: rejected(lambda: module.handoff_snapshot(source, contract_path, target)))
    altered = [
        ("artifact_id", "wrong"), ("artifact_version", "v1"), ("schema_version", "ad-event/v1"),
        ("source_kind", "ad-events"), ("rows", 99), ("sha256", "0" * 64),
        ("public_ids", [1]), ("public_fields", PUBLIC + ["user_id"]),
        ("captured_at", "2026-10-09T00:00:00+00:00"), ("kafka_position", {"offset": 1}),
        ("position_kind", "kafka-offset"),
        ("collector", "mysql-binlog"), ("binlog_cdc_status", "configured"),
        ("created_at", "2026-10-08T00:00:00"),
    ]
    for index, (field, value) in enumerate(altered):
        bad = root / f"bad-{index}.json"
        bad.write_text(json.dumps({**contract, field: value}), encoding="utf-8")
        output = root / f"bad-target-{index}"
        def fail(bad=bad, output=output):
            rejected(lambda: module.handoff_snapshot(source, bad, output))
            equal(output.exists(), False)
        checks.run(field + " 불일치 거절·최종폴더 없음", fail)

    def copy_failure():
        import shutil
        output = root / "copy-failure"
        real_copy = shutil.copyfile
        def corrupt(src, dst):
            real_copy(src, dst)
            Path(dst).write_bytes(b"corrupt\n")
        with patch.object(module.shutil, "copyfile", corrupt):
            rejected(lambda: module.handoff_snapshot(source, contract_path, output))
        equal(output.exists(), False)
        equal(list(root.glob(".copy-failure-*")), [])
    checks.run("복사 변조 감지·임시폴더 정리", copy_failure)
    command_target = root / "command-received"
    checks.run("인계 관리명령", lambda: equal(command("ads.management.commands.handoff_player_snapshot",
               source=str(source), contract=str(contract_path), target=str(command_target))["rows"], 2))
    checks.mutation("계약 검사 생략", lambda: rejected(lambda: {"rows": 99, "target": "created-without-check"}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--period", required=True, type=int, choices=range(1, 9))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    project = args.project.resolve()
    sys.path.insert(0, str(project))
    os.environ.pop("DJANGO_SETTINGS_MODULE", None)
    from django.conf import settings
    settings.configure(SECRET_KEY="day24-isolated-check", USE_TZ=True, TIME_ZONE="UTC",
                       DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
                       INSTALLED_APPS=(["django.contrib.auth", "django.contrib.contenttypes", "game"]
                                       if args.period == 1 else []))
    import django
    django.setup()
    checks = Checks()
    module_path = (project / "game/management/commands/export_player_snapshot.py" if args.period == 1
                   else project / "ads/snapshot_intake.py")
    tracked = [module_path]
    if args.period != 1:
        command_names = {2: "inspect_player_snapshot", 3: "write_cdc_readiness", 4: "write_player_change_fixture",
                         5: "write_snapshot_contract", 6: "compare_player_snapshots", 7: "read_snapshot_missing",
                         8: "handoff_player_snapshot"}
        tracked.append(project / f"ads/management/commands/{command_names[args.period]}.py")
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked if path.exists()}
    try:
        if args.period != 1:
            mongo = importlib.import_module("ads.mongo")
            def forbidden(*_args, **_kwargs):
                raise AssertionError("이 검사에서는 실제 Mongo 연결을 사용하지 않습니다.")
            mongo.get_db = forbidden
            mongo.get_client = forbidden
            mongo.MongoClient = forbidden
            module = importlib.import_module("ads.snapshot_intake")
        else:
            module = None
        with tempfile.TemporaryDirectory(prefix="day24-check-") as folder:
            root = Path(folder)
            tests = {1: test_one, 2: test_two, 3: test_three, 4: test_four,
                     5: test_five, 6: test_six, 7: test_seven, 8: test_eight}
            if args.period == 1:
                tests[1](checks, root)
            else:
                tests[args.period](checks, module, root)
    except Exception as exc:
        checks.results.append({"name": "저장 코드 로드·검사 준비", "passed": False,
                               "error": f"{type(exc).__name__}: {exc}"})
    after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked if path.exists()}
    checks.run("학생 저장 파일 변경 없음", lambda: equal(after, before))
    failures = sum(not result["passed"] for result in checks.results)
    report = {"period": args.period, "project": str(project), "passed": len(checks.results) - failures,
              "failed": failures, "database": "sqlite-memory-only", "mongo": "not-connected",
              "student_sources_unchanged": after == before, "source_sha256": after, "checks": checks.results}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
