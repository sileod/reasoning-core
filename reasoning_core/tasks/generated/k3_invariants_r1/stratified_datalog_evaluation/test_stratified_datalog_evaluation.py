import json
import random

from reasoning_core.tasks.generated.k3_invariants_r1.stratified_datalog_evaluation.stratified_datalog_evaluation import (
    StratifiedDatalogConfig,
    StratifiedDatalogEvaluation,
    parse_answer,
)


def _make(level, seed):
    return StratifiedDatalogEvaluation(StratifiedDatalogConfig(level=level, seed=seed))


def test_gold_scores_one():
    for level in range(7):
        random.seed(100 + level)
        task = _make(level, 100 + level)
        for _ in range(10):
            e = task.generate_entry()
            assert float(task.score_answer(e.answer, e)) == 1.0


def test_junk_scores_zero():
    random.seed(5)
    task = _make(2, 5)
    e = task.generate_entry()
    assert float(task.score_answer("", e)) == 0.0
    assert float(task.score_answer("garbage", e)) == 0.0


def test_answer_domain():
    random.seed(7)
    for level in [0, 3, 6]:
        task = _make(level, 7)
        for _ in range(20):
            e = task.generate_entry()
            q = e.metadata["query"]
            qidx = e.metadata["pred_names"].index(q)
            arity = e.metadata["arities"][qidx]
            parsed = parse_answer(e.answer, q, arity)
            assert parsed is not None
            assert all(len(a) == arity for a in parsed)
            assert parsed == sorted(parsed)


def test_config_difficulty():
    task = _make(0, 1)
    base = task.config.num_rules
    task.config.set_level(6)
    assert task.config.num_rules > base


def test_summary_and_design_choice():
    task = StratifiedDatalogEvaluation()
    assert "strata" in task.summary
    assert task.design_choice.startswith("Answer form:")


def test_score_survives_json_roundtrip():
    random.seed(42)
    for level in [0, 3, 6]:
        task = _make(level, 42)
        e = task.generate_entry()
        meta = json.loads(json.dumps(e.metadata))
        rebuilt = type("R", (), {"metadata": meta})()
        assert float(task.score_answer(e.answer, rebuilt)) == 1.0
