import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.rounded_display_consistency.rounded_display_consistency import (
    RoundedDisplayConsistency,
    _round_display,
    _multiple_bounds,
    _tight_range,
    _format_answer,
)


def test_round_half_even_display():
    assert _round_display(5, 2, "half_even") == 4
    assert _round_display(4, 2, "half_even") == 4
    assert _round_display(7, 2, "half_even") == 8


def test_round_tie_rules():
    assert _round_display(5, 2, "half_up") == 6
    assert _round_display(5, 2, "half_down") == 4
    assert _round_display(7, 2, "half_even") == 8


def test_bounds_consistent_with_display():
    for tie in ("half_up", "half_down", "half_even"):
        for inc in (1, 2, 3, 5, 7):
            for z in range(-30, 31):
                D = _round_display(z, inc, tie)
                b = _multiple_bounds(D, inc, tie)
                assert b is not None and b[0] <= z <= b[1]


def test_consistent_instance_solves():
    task = RoundedDisplayConsistency()
    for _ in range(50):
        e = task.generate_example()
        assert e.answer == _format_answer(e.metadata["feasible"],
                                           e.metadata["lo"], e.metadata["hi"])
        assert task.score_answer(e.answer, e) == 1.0
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("garbage", e) == 0.0


def test_both_answer_regimes_present():
    task = RoundedDisplayConsistency()
    answers = set()
    for _ in range(80):
        e = task.generate_example()
        answers.add(e.answer == "no")
    assert True in answers and False in answers


def test_metadata_json_serializable():
    import json
    task = RoundedDisplayConsistency()
    for _ in range(10):
        e = task.generate_example()
        json.dumps(e.metadata)


def test_all_levels_generate():
    task = RoundedDisplayConsistency()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            e = task.generate_example()
            assert e.answer in ("no",) or e.answer[0] == "["


def test_difficulty_changes_config():
    task = RoundedDisplayConsistency()
    task.config.set_level(0)
    e0 = task.config.latent_extent
    task.config.set_level(6)
    e6 = task.config.latent_extent
    assert e6 > e0


def test_sample_script_reproducible(tmp_path):
    import os, shutil, subprocess, sys
    script = Path(__file__).with_name("generate_samples_P008v2.py")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parents[5])
    outputs = []
    for tag in ("a", "b"):
        d = tmp_path / tag
        d.mkdir()
        dst = d / script.name
        dst.write_text(script.read_text())
        subprocess.run(
            [sys.executable, str(dst)], check=True, env=env,
            cwd=str(tmp_path),
        )
        outputs.append((d / "samples_P008v2.md").read_bytes())
    assert outputs[0] == outputs[1]
