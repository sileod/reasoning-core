import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from pooled_test_status_decoding import (
    PooledTestStatusDecode,
    _solve_statuses,
)


def test_prompt_determines_answer():
    task = PooledTestStatusDecode()
    task.config.set_level(3)
    seen = {}
    for _ in range(50):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        assert prompt in seen or entry.answer == seen.get(prompt, entry.answer)
        seen[prompt] = entry.answer


def test_difficulty_changes_config():
    task = PooledTestStatusDecode()
    task.config.set_level(0)
    n0 = task.config.n
    task.config.set_level(5)
    assert task.config.n > n0
    assert task.config.k >= 1
    task.config.set_level(0)
    assert task.config.n == n0


def test_answers_valid():
    task = PooledTestStatusDecode()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            ans = entry.answer
            assert len(ans) == entry.metadata["n"]
            assert set(ans) <= {"C", "T", "?"}
            for i, ch in enumerate(ans):
                if ch == "C":
                    assert i not in entry.metadata["positives"]
                elif ch == "T":
                    assert i in entry.metadata["positives"]
    assert 1.0 == task.score_answer(entry.answer, entry)
    assert task.score_answer("", entry) < 1.0


def test_label_balance():
    task = PooledTestStatusDecode()
    counts = {a: 0 for a in ("C", "T")}
    for _ in range(200):
        entry = task.generate_example()
        answer = entry.answer
        if "C" in answer:
            counts["C"] += 1
        if "T" in answer:
            counts["T"] += 1
    assert counts["C"] > 20
    assert counts["T"] > 20


def test_solver_agrees():
    task = PooledTestStatusDecode()
    task.config.set_level(4)
    for _ in range(30):
        entry = task.generate_example()
        n = entry.metadata["n"]
        k = entry.metadata["k"]
        pools = entry.metadata["pools"]
        pos = set(entry.metadata["positives"])
        status = _solve_statuses(n, k, [set(p) for p in pools], pos)
        assert status is not None
        assert "".join(status) == entry.answer
