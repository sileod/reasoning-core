import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rely_guarantee_compatibility import RelyGuaranteeCompatibility, _compute_violation


def test_balance_and_roundtrip():
    random.seed(1)
    task = RelyGuaranteeCompatibility()
    answers = set()
    for _ in range(60):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        answers.add(ex.answer)
    assert "none" in answers
    assert len(answers) >= 2


def test_empty_and_junk():
    random.seed(2)
    task = RelyGuaranteeCompatibility()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("zz", ex) < 1.0


def test_violation_matches_computation():
    random.seed(3)
    task = RelyGuaranteeCompatibility()
    for _ in range(80):
        ex = task.generate_example()
        meta = ex.metadata
        comps = {int(k): v for k, v in meta["components"].items()}
        computed = _compute_violation(comps, meta["n_components"])
        if ex.answer == "none":
            assert computed == "none"
        else:
            assert computed == ex.answer


def test_all_levels():
    random.seed(5)
    task = RelyGuaranteeCompatibility()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_matches_semantics():
    random.seed(11)
    task = RelyGuaranteeCompatibility()
    for _ in range(120):
        ex = task.generate_example()
        meta = ex.metadata
        comps = {int(k): v for k, v in meta["components"].items()}
        n = meta["n_components"]
        if ex.answer == "none":
            assert _compute_violation(comps, n) == "none"
        else:
            assert _compute_violation(comps, n) == ex.answer
            worst = None
            for i in range(n):
                if ex.answer in comps[i]["avars"]:
                    guarantees = set()
                    for j in range(n):
                        if j != i:
                            guarantees |= set(comps[j]["gvars"])
                    if ex.answer not in guarantees and (worst is None or (i, ex.answer) < worst):
                        worst = (i, ex.answer)
            assert worst is not None
