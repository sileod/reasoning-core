import random

from reasoning_core.tasks.generated.k3_relevance_separation_r1.schwartz_zippel_identity.schwartz_zippel_identity import (
    SchwartzZippelIdentity,
    SchwartzZippelConfig,
)


def test_gold_answers_score_full():
    task = SchwartzZippelIdentity()
    task.config = SchwartzZippelConfig()
    for _ in range(200):
        random.seed(_)
        e = task.generate_entry()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    task = SchwartzZippelIdentity()
    task.config = SchwartzZippelConfig()
    random.seed(0)
    e = task.generate_entry()
    for junk in ["", "maybe", "42", "YES ", "No"]:
        pass
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("maybe", e) == 0.0
    assert task.score_answer("42", e) == 0.0


def test_score_is_case_and_space_insensitive():
    task = SchwartzZippelIdentity()
    task.config = SchwartzZippelConfig()
    random.seed(1)
    e = task.generate_entry()
    assert task.score_answer(e.answer.upper(), e) == 1.0
    assert task.score_answer(" " + e.answer + " ", e) == 1.0


def test_label_balance():
    task = SchwartzZippelIdentity()
    task.config = SchwartzZippelConfig()
    random.seed(2)
    counts = {"yes": 0, "no": 0}
    for _ in range(500):
        random.seed(_)
        e = task.generate_entry()
        counts[e.answer] += 1
    assert 200 <= counts["yes"] <= 300, counts


def test_ground_truth_matches_polynomial_ids():
    task = SchwartzZippelIdentity()
    task.config = SchwartzZippelConfig()
    for seed in range(100):
        random.seed(seed)
        e = task.generate_entry()
        p = e.metadata["prime"]
        a = e.metadata["a"]
        b = e.metadata["b"]
        x = e.metadata["x"]
        from functools import reduce

        def ev(cs):
            acc = 0
            for c in reversed(cs):
                acc = (acc * x + c) % p
            return acc

        identical = (a == b)
        label = "yes" if identical else "no"
        assert e.answer == label


def test_difficulty_changes():
    cfg = SchwartzZippelConfig()
    base_prime = cfg.prime
    cfg.set_level(6)
    assert cfg.prime != base_prime or cfg.instances != SchwartzZippelConfig().instances
