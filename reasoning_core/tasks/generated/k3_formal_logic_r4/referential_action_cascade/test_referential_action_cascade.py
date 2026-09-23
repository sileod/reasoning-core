import random

from reasoning_core.tasks.generated.k3_formal_logic_r4.referential_action_cascade.referential_action_cascade import (
    Config,
    ReferentialActionCascade,
    _build_instance,
    simulate,
)


def _example(task, level):
    cfg = Config()
    cfg.set_level(level)
    task.config = cfg
    return task.generate_example()


def test_generate_and_score():
    random.seed(2072234021)
    task = ReferentialActionCascade()
    counts = {}
    for _ in range(200):
        e = _example(task, random.randrange(7))
        assert task.score_answer(e.answer, e) == 1.0
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("nonsense", e) == 0.0
        assert task.score_answer("3:restrict", e) == (1.0 if e.answer == "3:restrict" else 0.0)
        counts[e.answer] = counts.get(e.answer, 0) + 1
    assert "accepted" in counts
    assert len([k for k in counts if k != "accepted"]) > 0


def test_balanced_labels_not_constant():
    random.seed(99)
    task = ReferentialActionCascade()
    acc = rej = 0
    distinct = set()
    for _ in range(300):
        e = _example(task, 2)
        distinct.add(e.answer)
        if e.answer == "accepted":
            acc += 1
        else:
            rej += 1
    assert acc > 0 and rej > 0
    frac = acc / (acc + rej)
    assert 0.10 < frac < 0.60
    assert len(distinct) >= 5


def test_answer_variety():
    random.seed(1234)
    task = ReferentialActionCascade()
    distinct = set()
    for _ in range(300):
        e = _example(task, random.randrange(7))
        distinct.add(e.answer)
    assert len(distinct) >= 8


def test_all_levels():
    random.seed(7)
    task = ReferentialActionCascade()
    for level in range(7):
        for _ in range(20):
            e = _example(task, level)
            assert task.score_answer(e.answer, e) == 1.0


def test_simulator_matches_gold():
    random.seed(2024)
    task = ReferentialActionCascade()
    cfg = Config()
    cfg.set_level(3)
    task.config = cfg
    e = task.generate_example()
    schema = {
        "tables": e.metadata["tables"],
        "fks": e.metadata["fks"],
        "seed": e.metadata["seed"],
    }
    stmts = list(e.metadata["statements"])
    res, idx, reason = simulate(schema, stmts)
    if res == "ok":
        assert e.answer == "accepted"
    else:
        assert e.answer == f"{idx}:{reason}"


def test_simulator_reproducible():
    random.seed(555)
    task = ReferentialActionCascade()
    cfg = Config()
    cfg.set_level(3)
    task.config = cfg
    e1 = task.generate_example()
    random.seed(555)
    task2 = ReferentialActionCascade()
    task2.config = Config()
    task2.config.set_level(3)
    e2 = task2.generate_example()
    assert e1.answer == e2.answer
    assert e1.metadata["statements"] == e2.metadata["statements"]


def test_violation_reason_valid():
    random.seed(777)
    task = ReferentialActionCascade()
    for _ in range(400):
        e = _example(task, random.randrange(7))
        if e.answer == "accepted":
            continue
        idx, reason = e.answer.split(":")
        assert reason in {"restrict", "cascade", "set-null", "set-default"}
        assert int(idx) >= 0


def test_build_instance_produces_valid_prefix():
    random.seed(31337)
    for level in range(7):
        cfg = Config()
        cfg.set_level(level)
        random.seed(31337 + level)
        schema, stmts = _build_instance(cfg)
        table_ids = {}
        schema2 = {"tables": schema["tables"], "fks": schema["fks"], "seed": schema["seed"]}
        res, idx, reason = simulate(schema2, stmts)
        assert res in ("ok", "reject")
