import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from reasoning_core.evaluation.battery import load_battery_manifest


RESOURCES = Path(__file__).resolve().parents[2] / "reasoning_core" / "resources"


def test_packaged_nomenu_cloze_suite(tmp_path):
    battery = load_battery_manifest(RESOURCES / "batteries/nomenu_cloze_v1.json", tmp_path)
    assert {leg.name for leg in battery.legs} == {
        "sciq", "arc_easy", "arc_challenge", "boolq", "commonsenseqa", "hellaswag",
        "mmlu_all_nomenu_cloze", "openbookqa", "piqa", "socialiqa", "winogrande",
    }
    with zipfile.ZipFile(RESOURCES / "battery_legs.zip") as archive:
        assert len(archive.namelist()) == len(set(archive.namelist()))
    for leg in battery.legs:
        assert leg.kind == "mcq"
        rows = [json.loads(line) for line in Path(leg.path).read_text().splitlines()]
        if leg.limit:
            rows = rows[:leg.limit]
        if leg.keep is not None:
            rows = [rows[i] for i in leg.keep]
        assert rows
        seen = set()
        for row in rows:
            assert row["answer"] == row["choices"][row["answer_idx"]]
            assert len(set(row["choices"])) == len(row["choices"]) >= 2
            assert all(choice.strip() for choice in row["choices"])
            assert not re.search(r"(?m)^\s*[A-D][.)]\s+", row["prompt"])
            key = row["prompt"].strip(), tuple(sorted(row["choices"]))
            assert key not in seen
            seen.add(key)
        if leg.name == "mmlu_all_nomenu_cloze":
            counts = Counter(row["subject"] for row in rows)
            assert len(counts) == 57
            assert set(counts.values()) == {18}
        if leg.name == "socialiqa":
            assert len(rows) == 594
    assert battery.identifier.startswith("nomenu_cloze_v1/battery@v1:")


def test_historical_full_battery_identity_is_preserved(tmp_path):
    battery = load_battery_manifest(
        RESOURCES / "batteries/copyfree_battery_v8.json", tmp_path, max_length=1024)
    assert battery.identifier == "copyfree_battery_v8/battery@v1:1a482a2aeb5d"
