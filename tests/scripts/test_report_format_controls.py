import importlib.util
from pathlib import Path

import pytest


path = Path(__file__).parents[2] / "scripts/report_format_controls.py"
spec = importlib.util.spec_from_file_location("report_format_controls", path)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def row(question="Question", menu=False, choices=("yes", "no"), gold=0):
    return {"prompt": question + ("\nOptions:\n(A) yes\n(B) no" if menu else ""),
            "choices": list(choices), "answer_idx": gold, "answer": choices[gold]}


def test_join_is_one_to_one_and_preserves_choice_identity():
    source = [row(menu=True), row(menu=True), row(choices=("no", "yes"), gold=1)]
    assert report.match_items(source, [row()]) == [(0, 0)]


def test_different_item_sets_are_not_called_format_controls():
    source, target = [row("one")], [row("two")]
    result = report.contrast(source, target, {}, {}, "menu", "nomenu")
    assert result["status"] == "no matched format change"
    assert result["matched_items"] == 0


def test_identical_prompts_do_not_create_a_format_effect():
    result = report.contrast([row()], [row()], {}, {}, "menu", "nomenu")
    assert result["matched_items"] == 1
    assert result["changed_prompt_items"] == 0


def test_format_contrast_subtracts_baseline_and_uses_matched_indices():
    source, target = [row("one", True), row("two", True)], [row("two"), row("one")]
    baseline = {"menu": {"prediction": [1, 1], "margin": [-2, -2]},
                "nomenu": {"prediction": [1, 1], "margin": [-1, -1]}}
    treatment = {"menu": {"prediction": [0, 0], "margin": [1, 1]},
                 "nomenu": {"prediction": [1, 0], "margin": [0, 1]}}
    result = report.contrast(source, target, baseline, treatment, "menu", "nomenu")
    effects = result["menu_effect_on_transfer"]
    assert effects["accuracy_pp"]["mean"] == 50
    assert effects["margin"]["mean"] == 1.5
    transfer = result["transfer_on_matched_items"]
    assert transfer["menu"]["accuracy_pp"]["mean"] == 100
    assert transfer["nomenu"]["accuracy_pp"]["mean"] == 50
    assert transfer["nomenu"]["margin"]["mean"] == 1.5


def test_sidecar_alignment_errors_are_not_silently_truncated():
    bad = {"menu": {"prediction": [], "margin": []},
           "nomenu": {"prediction": [0], "margin": [0]}}
    with pytest.raises(ValueError, match="counts differ"):
        report.contrast([row(menu=True)], [row()], bad, bad, "menu", "nomenu")


def test_sidecar_join_requires_battery_and_seed_identity():
    good = {"battery_id": "battery", "seed": 43, "metrics": {"acc": 0.5}, "legs": {}}
    stale = {**good, "battery_id": "old-battery"}
    other_seed = {**good, "seed": 44}
    assert report.find_sidecar([stale, other_seed, good], {"acc": 0.5}, "battery", 43) == {}
    with pytest.raises(ValueError, match="found 0"):
        report.find_sidecar([stale, other_seed], {"acc": 0.5}, "battery", 43)


def test_corrected_manifest_has_unique_items_and_identical_format_pairs(tmp_path):
    import json
    from reasoning_core.evaluation.battery import ensure_eval_data, load_battery_manifest

    data = ensure_eval_data(tmp_path)
    manifest = path.parents[1] / "reasoning_core/resources/batteries/transfer_controls_v1.json"
    battery = load_battery_manifest(manifest, data)
    assert battery.max_length == 1024
    legs = json.loads(manifest.read_text())["legs"]
    rows = {leg["name"]: report.load_rows(leg, data) for leg in legs}
    for name, items in rows.items():
        keys = [report.item_key(item) for item in items]
        assert len(keys) == len(set(keys)), name
    assert len(rows["mmlu_high_school_math_nomenu"]) == 265
    assert len(rows["mmlu_other_cloze"]) == 398
    for split, count in (("dev", 220), ("test", 100)):
        menu, nomenu = rows[f"bbh_{split}_menu"], rows[f"bbh_{split}_nomenu"]
        assert len(menu) == len(nomenu) == count
        assert [report.item_key(r) for r in menu] == [report.item_key(r) for r in nomenu]
        assert all(a["prompt"] != b["prompt"] for a, b in zip(menu, nomenu))
