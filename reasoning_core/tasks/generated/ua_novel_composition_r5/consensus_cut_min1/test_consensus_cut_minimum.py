import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from consensus_cut_minimum import ConsensusCutMin1, compute_min_cuts


def test_generate_example():
    task = ConsensusCutMin1()
    ex = task.generate_example()
    assert ex.answer is not None
    assert int(ex.answer) >= 0
    assert ex.metadata["segments"]


def test_gold_scores_one():
    task = ConsensusCutMin1()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = ConsensusCutMin1()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("banana", ex) == 0.0
    assert task.score_answer("IMPOSSIBLE", ex) == 0.0


def test_brute_force_runs():
    assert compute_min_cuts(5, [(0, 4, 1), (1, 3, 2)]) is not None


def test_multi_levels():
    task = ConsensusCutMin1()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_known_single_cut():
    assert compute_min_cuts(6, [(1, 3, 3), (0, 4, 3)]) == 1


def test_known_answer_range():
    task = ConsensusCutMin1()
    task.config.set_level(5)
    seen = set()
    for _ in range(40):
        ex = task.generate_example()
        seen.add(int(ex.answer))
    assert len(seen) >= 2


def test_min_is_valid_feasible():
    task = ConsensusCutMin1()
    task.config.set_level(5)
    ex = task.generate_example()
    a = int(ex.answer)
    assert a >= 1
    assert compute_min_cuts(ex.metadata["n"], ex.metadata["segments"]) == a


def test_weight_irrelevant_to_min():
    task = ConsensusCutMin1()
    ex = task.generate_example()
    seg0 = [tuple(s) for s in ex.metadata["segments"]]
    a0 = compute_min_cuts(ex.metadata["n"], seg0)
    seg1 = [(s, e, 1) for (s, e, _) in seg0]
    assert compute_min_cuts(ex.metadata["n"], seg1) == a0
