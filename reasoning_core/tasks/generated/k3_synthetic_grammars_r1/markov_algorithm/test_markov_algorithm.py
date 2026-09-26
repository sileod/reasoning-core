import json
import random

from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.markov_algorithm.markov_algorithm import (
    MarkovAlgorithm,
    MarkovAlgorithmConfig,
    _simulate,
)


def test_simulate_single_rule_leftmost():
    rules = [("ab", "", False)]
    steps, fired, halted = _simulate("abab", rules, 100)
    assert halted is False
    # Leftmost ab removed each time: abab -> ab -> "", two applications.
    assert steps == 2 and fired == [0, 0]


def test_simulate_dot_rule_halts():
    rules = [("b", "", True), ("a", "x", False)]
    steps, fired, halted = _simulate("ba", rules, 100)
    # First rule (b -> .) fires once; leftmost b applies and halts.
    assert halted is True and steps == 1 and fired == [0]


def test_simulate_first_matching_rule_wins():
    rules = [("ab", "x", False), ("a", "y", False)]
    steps, fired, halted = _simulate("aab", rules, 100)
    # Rule 1 matches "ab", rule 2 matches "a". First rule wins: aab -> ax,
    # then rule 2 "a"? new word "ax": rule1 no, rule2 yes -> yx. then no match.
    assert halted is False and steps == 2 and fired == [0, 1]


def test_generate_entry_shape_and_validity():
    random.seed(12345)
    task = MarkovAlgorithm()
    entry = task.generate_example()
    assert isinstance(entry.answer, str) and entry.answer.isdigit()
    md = dict(entry.metadata)
    json.dumps(md)
    steps, fired, halted = _simulate(md["word"], [tuple(r) for r in md["rules"]], 10000)
    assert md["steps"] == steps
    assert str(steps) == entry.answer
    assert steps == int(entry.answer)


def test_junk_answers_do_not_score():
    random.seed(7)
    task = MarkovAlgorithm()
    entry = task.generate_example()
    for bad in ("", "reajrjrje9595!", "0", "None", "True"):
        if bad != entry.answer:
            assert task.score_answer(bad, entry) < 1
    assert task.score_answer(entry.answer, entry) == 1


def test_difficulty_scales():
    cfg = MarkovAlgorithmConfig()
    cfg.set_level(0)
    c0 = (cfg.word_min, cfg.n_rules, cfg.max_pat_len, cfg.min_steps)
    cfg.set_level(6)
    c6 = (cfg.word_min, cfg.n_rules, cfg.max_pat_len, cfg.min_steps)
    assert c0 != c6
    for a, b in zip(c0, c6):
        assert b >= a


def test_label_diversity_across_levels():
    random.seed(999)
    task = MarkovAlgorithm()
    seen = set()
    for level in (0, 2, 5):
        for _ in range(25):
            e = task.generate_example(level=level)
            seen.add(e.answer)
    assert len(seen) >= 5


def test_no_reseed():
    random.seed(4242)
    task = MarkovAlgorithm()
    task.generate_example()
    r1 = random.random()
    task.generate_example()
    r2 = random.random()
    assert r1 != r2
