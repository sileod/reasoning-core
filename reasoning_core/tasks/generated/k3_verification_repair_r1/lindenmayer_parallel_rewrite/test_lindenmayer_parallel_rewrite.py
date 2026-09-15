import random

from reasoning_core.tasks.generated.k3_verification_repair_r1.lindenmayer_parallel_rewrite.lindenmayer_parallel_rewrite import (
    LindenmayerConfig,
    LindenmayerParallelRewrite,
    _expected_count,
)


def test_generate_and_score():
    task = LindenmayerParallelRewrite()
    x = task.generate_example()
    assert int(x.answer) >= 0
    assert task.score_answer(x.answer, x) == 1.0


def test_rejects_junk():
    task = LindenmayerParallelRewrite()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("abc", x) < 1.0
    assert task.score_answer("-5", x) < 1.0


def test_expected_count_matches_answer():
    task = LindenmayerParallelRewrite()
    for _ in range(20):
        x = task.generate_example()
        md = x.metadata
        productions = {}
        for a in ["A", "B", "C"]:
            items = md["productions"][a]
            chosen = []
            probs = []
            for item in items:
                sym, p = item.split(":")
                chosen.append(sym)
                probs.append(float(p))
            productions[a] = (chosen, probs)
        expect = _expected_count(
            md["initial"], productions, md["terminal_symbol"], md["steps"]
        )
        assert abs(expect - int(x.answer)) < 0.15


def test_difficulty_changes():
    task = LindenmayerParallelRewrite()
    base = LindenmayerConfig()
    base.set_level(0)
    lo = base.steps
    base.set_level(6)
    assert base.steps > lo


def test_deterministic_with_seed():
    random.seed(1)
    a = LindenmayerParallelRewrite().generate_entry()
    random.seed(1)
    b = LindenmayerParallelRewrite().generate_entry()
    assert a.answer == b.answer
    assert a.metadata == b.metadata
