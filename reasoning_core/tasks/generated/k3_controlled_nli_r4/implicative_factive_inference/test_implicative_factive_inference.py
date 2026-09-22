import random
from collections import Counter

from reasoning_core.tasks.generated.k3_controlled_nli_r4.implicative_factive_inference.implicative_factive_inference import (
    ImplicativeFactiveInference,
    _outcome,
    VERB_STATE,
    _asserted_state,
)


def test_generate_and_score_gold():
    task = ImplicativeFactiveInference()
    for _ in range(300):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
        assert x.metadata["label"] in ("ENTAILED", "DENIED", "OPEN")


def test_junk_and_empty_do_not_score():
    task = ImplicativeFactiveInference()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("banana", x) == 0.0
    assert task.score_answer(None, x) == 0.0
    assert task.score_answer("1.0", x) == 0.0


def test_outcome_domain_and_match_state():
    for verb, tbl in VERB_STATE.items():
        assert set(tbl.values()) <= {-1, 0, 1}
    for state in (-1, 0, 1):
        for cn in (True, False):
            out = _outcome(state, cn)
            assert out in ("ENTAILED", "DENIED", "OPEN")
    assert _outcome(1, False) == "ENTAILED"
    assert _outcome(1, True) == "DENIED"
    assert _outcome(-1, False) == "DENIED"
    assert _outcome(-1, True) == "ENTAILED"
    assert _outcome(0, True) == "OPEN"
    assert _outcome(0, False) == "OPEN"


def test_known_implicative_readings():
    # manage: negative polarity denies the complement
    assert _outcome(_asserted_state("manage", True), False) == "DENIED"
    # fail: negative polarity entails the complement
    assert _outcome(_asserted_state("fail", True), False) == "ENTAILED"
    # pretend positive: asserts complement false
    assert _outcome(_asserted_state("pretend", False), False) == "DENIED"
    # pretend negative: open
    assert _outcome(_asserted_state("pretend", True), False) == "OPEN"


def test_level_change_changes_config():
    task = ImplicativeFactiveInference()
    task.config.set_level(0)
    base = task.config.cond_prob
    task.config.set_level(6)
    hi = task.config.cond_prob
    assert hi > base


def test_label_balance_not_constant():
    task = ImplicativeFactiveInference()
    c = Counter(task.generate_example().metadata["label"] for _ in range(2000))
    assert len(c) == 3
    assert min(c.values()) > 0


def test_answer_format_matches_compare():
    task = ImplicativeFactiveInference()
    for _ in range(500):
        x = task.generate_example()
        if x.metadata["compare"]:
            assert x.answer in ("YES", "NO", "MAYBE")
        else:
            assert x.answer in ("ENTAILED", "DENIED", "OPEN")
