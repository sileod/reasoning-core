import random

from reasoning_core.tasks.generated.k3_counterfactual_r1.boolean_network_knockout.boolean_network_knockout import (
    BooleanNetworkKnockout,
    _step,
    _attractor,
)


def test_gold_scores_one(tmp_path):
    random.seed(1)
    task = BooleanNetworkKnockout()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_recompute_attractor():
    random.seed(42)
    task = BooleanNetworkKnockout()
    n = task.config.n
    x = task.generate_example()
    tables = [(tuple(d), c) for d, c in x.metadata["tables"]]
    start = tuple(x.metadata["start"])
    tn = x.metadata["target_node"]
    fv = x.metadata["fixed_val"]
    new_cyc, _ = _attractor(start, tables, (tn, fv))
    from reasoning_core.tasks.generated.k3_counterfactual_r1.boolean_network_knockout.boolean_network_knockout import (
        _normalize,
    )
    rep = [tuple((fv if i == tn else b) for i, b in enumerate(s)) for s in new_cyc]
    assert _normalize(rep) == _normalize(
        [tuple(s) for s in x.metadata["final_cycle"]]
    )


def test_junk_scores_zero():
    random.seed(7)
    task = BooleanNetworkKnockout()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0


def test_distractors_rejected():
    random.seed(3)
    task = BooleanNetworkKnockout()
    x = task.generate_example()
    for d in task.distractor_candidates(x):
        assert task.score_answer(d, x) == 0.0


def test_difficulty_changes():
    task = BooleanNetworkKnockout()
    task.config.set_level(0)
    n0, k0 = task.config.n, task.config.k
    task.config.set_level(6)
    n6, k6 = task.config.n, task.config.k
    assert n6 > n0
