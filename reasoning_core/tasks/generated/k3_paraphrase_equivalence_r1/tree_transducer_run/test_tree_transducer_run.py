import random

from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r1.tree_transducer_run.tree_transducer_run import (
    TreeTransducerRun,
    _run,
    _fmt_rule,
)


def _balanced_outcomes(seed, n=200):
    rng = random.Random(seed)
    outcomes = {"ok": 0, "stuck": 0}
    for _ in range(n):
        random.seed(rng.randrange(2**32))
        task = TreeTransducerRun()
        task.config.set_level(0)
        entry = task.generate_example()
        outcomes[entry.metadata["outcome"]] += 1
    return outcomes


def test_generate_and_score():
    task = TreeTransducerRun()
    for level in range(7):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    task = TreeTransducerRun()
    task.config.set_level(2)
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("some random text", x) == 0.0


def test_outcomes_balanced():
    out = _balanced_outcomes(11)
    total = out["ok"] + out["stuck"]
    assert total > 0
    assert out["ok"] / total > 0.2, out
    assert out["stuck"] / total > 0.2, out


def test_metadata_json_serializable():
    import json

    task = TreeTransducerRun()
    task.config.set_level(4)
    x = task.generate_example()
    json.dumps(x.metadata)


def test_reproducible():
    task = TreeTransducerRun()
    task.config.set_level(5)
    random.seed(42)
    a = task.generate_example()
    random.seed(42)
    b = task.generate_example()
    assert a.answer == b.answer
    pa = {k: v for k, v in a.metadata.items() if k not in ("_time",)}
    pb = {k: v for k, v in b.metadata.items() if k not in ("_time",)}
    assert pa == pb


def test_difficulty_changes_config():
    task = TreeTransducerRun()
    task.config.set_level(0)
    base = dict(task.config.__dict__)
    task.config.set_level(6)
    high = dict(task.config.__dict__)
    assert base != high


def test_gold_answer_reproduced_by_run():
    task = TreeTransducerRun()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            x = task.generate_example()
            rules = {
                tuple(key.split("/")): dict(rule)
                for key, rule in x.metadata["rules"].items()
            }
            status, result = _run(
                x.metadata["label_of"], x.metadata["children_of"], rules,
                x.metadata["start_state"],
            )
            expected_outcome = x.metadata["outcome"]
            if expected_outcome == "ok":
                assert status == "ok" and result == x.answer, (level, result, x.answer)
            else:
                assert status == "stuck" and result == x.answer, (level, result, x.answer)
