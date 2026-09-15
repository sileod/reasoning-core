import random
import numpy as np

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_verification_repair_r1.cellular_automaton_step.cellular_automaton_step import (
    CellularAutomatonStep,
    _rule_lookup,
    _step,
)


def _step_solver(row, rule, boundary, steps):
    n = len(row)
    cur = list(row)
    cur = [int(c) for c in cur]
    for _ in range(steps):
        nxt = []
        for i in range(n):
            if boundary == "periodic":
                left = cur[(i - 1) % n]
                center = cur[i]
                right = cur[(i + 1) % n]
            else:
                left = cur[i - 1] if i - 1 >= 0 else 0
                center = cur[i]
                right = cur[i + 1] if i + 1 < n else 0
            nxt.append(_rule_lookup(rule, left, center, right))
        cur = nxt
    return cur


def test_generate_example_returns_entry():
    task = CellularAutomatonStep()
    x = task.generate_example()
    assert isinstance(x, Entry)
    assert isinstance(x.answer, str)


def test_gold_answer_scores_1():
    task = CellularAutomatonStep()
    for _ in range(50):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_cell_mode_answer_is_valid():
    task = CellularAutomatonStep()
    for _ in range(50):
        x = task.generate_example()
        cfg = x.metadata
        assert isinstance(cfg["rule"], int)
        assert 0 <= cfg["rule"] <= 255
        assert cfg["mode"] in ("row", "cell", "count")
        if cfg["mode"] == "row":
            assert len(x.answer) == len(cfg["row"])
            assert set(x.answer) <= {"0", "1"}
        elif cfg["mode"] == "cell":
            assert x.answer in ("0", "1")
        else:
            assert int(x.answer) >= 0
            assert int(x.answer) <= len(cfg["row"])


def test_answer_matches_independent_solver():
    task = CellularAutomatonStep()
    for _ in range(100):
        x = task.generate_example()
        cfg = x.metadata
        final = _step_solver(cfg["row"], cfg["rule"], cfg["boundary"], cfg["steps"])
        if cfg["mode"] == "row":
            expected = "".join(map(str, final))
        elif cfg["mode"] == "cell":
            expected = str(final[cfg["query"]])
        else:
            expected = str(sum(final))
        assert x.answer == expected


def test_metadata_json_serializable():
    import json

    task = CellularAutomatonStep()
    for _ in range(30):
        x = task.generate_example()
        json.dumps(x.metadata)


def test_difficulty_changes_config():
    task = CellularAutomatonStep()
    before = (task.config.length, task.config.min_steps, task.config.max_steps)
    task.config.set_level(6)
    after = (task.config.length, task.config.min_steps, task.config.max_steps)
    assert before != after
    assert after[0] > before[0]


def test_score_rejects_wrong():
    task = CellularAutomatonStep()
    for _ in range(30):
        x = task.generate_example()
        wrong = "x" if x.answer != "x" else "y"
        assert task.score_answer(wrong, x) < 1.0
        assert task.score_answer("", x) < 1.0
