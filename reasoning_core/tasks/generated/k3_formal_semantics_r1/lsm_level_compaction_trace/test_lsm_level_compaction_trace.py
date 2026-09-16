import random

from reasoning_core.tasks.generated.k3_formal_semantics_r1.lsm_level_compaction_trace.lsm_level_compaction_trace import (
    LsmLevelCompactionTrace,
    _compact,
    _make_runs,
    _norm_pairs,
    _score_pairs,
)


def test_gold_scores_one():
    task = LsmLevelCompactionTrace()
    for _ in range(20):
        task.config.set_level(random.randint(0, 6))
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_wrong_score_zero():
    task = LsmLevelCompactionTrace()
    task.config.set_level(3)
    x = task.generate_example()
    tokens = x.answer.split()
    if x.answer == "empty":
        other = "30=1"
    else:
        k, v = tokens[0].split("=")
        other = f"{k}={int(v) + 1}" if int(v) + 1 != int(v) else f"{k}={int(v) + 1}"
    assert task.score_answer(other, x) == 0.0
    assert task.score_answer("junk", x) == 0.0
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("999=0", x) == 0.0


def test_almost_right_score_zero():
    task = LsmLevelCompactionTrace()
    task.config.set_level(1)
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_levels_vary_answer():
    task = LsmLevelCompactionTrace()
    answers = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(8):
            x = task.generate_example()
            answers.add(x.answer)
    assert len(answers) > 3


def test_none_global_reseed():
    import reasoning_core.tasks.generated.k3_formal_semantics_r1.lsm_level_compaction_trace.lsm_level_compaction_trace as m

    task = m.LsmLevelCompactionTrace()
    task.config.set_level(2)
    random.seed(0)
    a1 = task.generate_example().answer
    random.seed(0)
    a2 = task.generate_example().answer
    assert a1 == a2


def test_compaction_shadows_versions():
    ops = [(5, "put", 10, 0), (5, "put", 99, 1), (7, "put", 3, 2)]
    assert _compact([_make_runs(ops, 3)[0]]) == "5=99 7=3"


def test_compaction_drops_tombstone():
    ops = [(5, "put", 10, 0), (5, "del", None, 1), (7, "put", 3, 2)]
    assert _compact([_make_runs(ops, 3)[0]]) == "7=3"


def test_compaction_across_runs():
    ops1 = [(5, "put", 10, 0)]
    ops2 = [(5, "del", None, 1)]
    ops3 = [(5, "put", 8, 2), (9, "del", None, 3)]
    runs = [_make_runs(ops1, 1)[0], _make_runs(ops2, 1)[0], _make_runs(ops3, 1)[0]]
    assert _compact(runs) == "5=8"


def test_score_pairs():
    assert _score_pairs("3=40 8=11", "3=40 8=11") == 1.0
    assert _score_pairs(" 8=11 3=40 ", "3=40 8=11") == 1.0
    assert _score_pairs("empty", "empty") == 1.0
    assert _score_pairs("3=40", "3=40 8=11") == 0.0
    assert _score_pairs("", "3=40") == 0.0
    assert _score_pairs("junk", "3=40") == 0.0


def test_norm_pairs():
    assert _norm_pairs("empty") == ()
    assert _norm_pairs("") == ()
    assert _norm_pairs("9=1 2=3") == ("2=3", "9=1")


def test_validate():
    task = LsmLevelCompactionTrace()
    task.validate()
