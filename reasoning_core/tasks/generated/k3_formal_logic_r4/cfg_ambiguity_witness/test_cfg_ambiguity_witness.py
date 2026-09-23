import random

from reasoning_core.tasks.generated.k3_formal_logic_r4.cfg_ambiguity_witness import (
    cfg_ambiguity_witness as mod,
)


def test_gold_scores_one():
    random.seed(123)
    task = mod.CFGAmbiguityWitness()
    for _ in range(20):
        e = task.generate_entry()
        assert task.score_answer(e.answer, e) == 1.0


def test_answers_balanced():
    random.seed(7)
    task = mod.CFGAmbiguityWitness()
    counts = {"yes": 0, "no": 0}
    for _ in range(60):
        e = task.generate_entry()
        if e.answer.startswith("yes"):
            counts["yes"] += 1
        else:
            counts["no"] += 1
    assert counts["yes"] >= 10 and counts["no"] >= 10


def test_junk_does_not_score():
    random.seed(5)
    task = mod.CFGAmbiguityWitness()
    for _ in range(20):
        e = task.generate_entry()
        assert task.score_answer("", e) < 1.0
        assert task.score_answer("garbage input", e) < 1.0


def test_level_scaling():
    task = mod.CFGAmbiguityWitness()
    task.config.set_level(0)
    l0 = task.config.max_len
    task.config.set_level(6)
    l6 = task.config.max_len
    assert l6 > l0


def test_witness_correct():
    random.seed(11)
    task = mod.CFGAmbiguityWitness()
    for _ in range(30):
        e = task.generate_entry()
        if e.metadata["ambiguous"]:
            w = e.metadata["word"]
            assert mod._num_parse_trees(tuple(w), e.metadata["rules"], set(e.metadata["terminals"])) >= 2
        else:
            assert e.answer == "no"
