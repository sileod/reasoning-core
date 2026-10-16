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


def test_chat_template_battery_is_a_separate_identity(tmp_path):
    rows = json.loads((RESOURCES / "batteries/copyfree_battery_v13_tiny.json").read_text())
    rows = {**rows, "legs": [leg for leg in rows["legs"] if leg["name"] in ("arc_easy", "sciq")]}
    (tmp_path / "raw.json").write_text(json.dumps(rows))
    (tmp_path / "chat.json").write_text(json.dumps({**rows, "chat_template": True}))
    raw = load_battery_manifest(tmp_path / "raw.json", tmp_path)
    chat = load_battery_manifest(tmp_path / "chat.json", tmp_path)
    assert not raw.chat_template and chat.chat_template
    assert [leg.identifier for leg in raw.legs] == [leg.identifier for leg in chat.legs]
    assert raw.identifier.split(":")[1] != chat.identifier.split(":")[1]


def test_chat_template_prompt_is_a_user_turn():
    from reasoning_core.evaluation.metrics import _prompt_ids

    class Tok:
        def __call__(self, text, add_special_tokens=False):
            return {"input_ids": [ord(c) for c in text]}

        def apply_chat_template(self, messages, add_generation_prompt, tokenize):
            assert add_generation_prompt and tokenize
            return [ord(c) for c in f"<u>{messages[0]['content']}</u><a>"]

    decode = lambda ids: "".join(map(chr, ids))
    assert decode(_prompt_ids(Tok(), "Q?\n")) == "Q?\n"
    assert decode(_prompt_ids(Tok(), "Q?\n", chat_template=True)) == "<u>Q?</u><a>"


def test_v13_batteries_rebuild_from_the_shipped_legs(tmp_path):
    for name, digest in (("copyfree_battery_v13_tiny", "8721e42db0ed"),
                         ("copyfree_battery_v13_tiny_chat", "c1d446a84e93")):
        battery = load_battery_manifest(RESOURCES / f"batteries/{name}.json", tmp_path, max_length=1024)
        assert battery.identifier == f"{name}/battery@v1:{digest}"
