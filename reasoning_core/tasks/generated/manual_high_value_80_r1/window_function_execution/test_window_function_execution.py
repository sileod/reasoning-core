import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from reasoning_core.tasks.generated.manual_high_value_80_r1.window_function_execution.window_function_execution import (  # noqa: E402
    WindowFunctionExecution,
    WindowFunctionConfig,
)


def _score(task, entry, answer):
    return task.score_answer(answer, entry)


def test_gold_scores():
    random.seed(1)
    for level in (0, 2, 5):
        task = WindowFunctionExecution()
        cfg = WindowFunctionConfig()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(20):
            entry = task.generate_entry()
            assert _score(task, entry, entry.answer) == 1.0


def test_junk_scores_zero():
    random.seed(2)
    task = WindowFunctionExecution()
    cfg = WindowFunctionConfig()
    cfg.set_level(3)
    task.config = cfg
    for _ in range(30):
        entry = task.generate_entry()
        assert _score(task, entry, "") == 0.0
        assert _score(task, entry, "notananswer") == 0.0


def test_all_modes_reachable():
    random.seed(3)
    seen = set()
    task = WindowFunctionExecution()
    cfg = WindowFunctionConfig()
    cfg.set_level(4)
    task.config = cfg
    for _ in range(300):
        entry = task.generate_entry()
        seen.add(entry.metadata["mode"])
    assert seen == {"running", "rank", "lag", "lead", "count", "sum", "avg"}


def test_label_balance():
    random.seed(4)
    task = WindowFunctionExecution()
    cfg = WindowFunctionConfig()
    cfg.set_level(2)
    task.config = cfg
    none = 0
    total = 0
    for _ in range(400):
        entry = task.generate_entry()
        if entry.metadata["mode"] in ("lag", "lead") and entry.answer == "NONE":
            none += 1
        total += 1
    assert 0 < none < total


def test_difficulty_changes():
    c0 = WindowFunctionConfig()
    c0.set_level(0)
    c5 = WindowFunctionConfig()
    c5.set_level(5)
    assert c5.n_rows >= c0.n_rows
    assert c5.n_partitions >= c0.n_partitions


def test_gold_answer_reproducible_across_levels():
    random.seed(7)
    for level in (0, 1, 3, 6):
        task = WindowFunctionExecution()
        cfg = WindowFunctionConfig()
        cfg.set_level(level)
        task.config = cfg
        seen = set()
        for _ in range(15):
            entry = task.generate_entry()
            rows = tuple((r["part"], r["score"], r["tb"]) for r in entry.metadata["rows"])
            seen.add(rows)
        assert len(seen) >= 3


def test_running_consistency():
    random.seed(8)
    task = WindowFunctionExecution()
    cfg = WindowFunctionConfig()
    cfg.set_level(3)
    task.config = cfg
    for _ in range(100):
        entry = task.generate_entry()
        if entry.metadata["mode"] != "running":
            continue
        q = entry.metadata["query"]
        q_rows = [r for r in entry.metadata["rows"] if r["part"] == q["part"]]
        q_sorted = sorted(q_rows, key=lambda r: (r["score"], r["tb"], r["id"]))
        acc = 0
        for r in q_sorted:
            acc += r["score"]
            if r["id"] == q["id"]:
                break
        assert entry.answer == str(acc)


def test_avg_is_valid_decimal():
    random.seed(9)
    task = WindowFunctionExecution()
    cfg = WindowFunctionConfig()
    cfg.set_level(2)
    task.config = cfg
    for _ in range(200):
        entry = task.generate_entry()
        if entry.metadata["mode"] == "avg":
            val = float(entry.answer)
            assert val > 0
