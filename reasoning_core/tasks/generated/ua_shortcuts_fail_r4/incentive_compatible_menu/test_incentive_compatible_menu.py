import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.incentive_compatible_menu.incentive_compatible_menu import (
    IncentiveCompatibleMenu,
    _max_profit,
)


def test_gold_answer_scores_one():
    task = IncentiveCompatibleMenu()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            assert isinstance(entry, Entry)
            assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_and_empty_rejected():
    task = IncentiveCompatibleMenu()
    entry = task.generate_example()
    for bad in ("", " ", "abc", "-3", "1.5", "reajrjrje9595!"):
        assert task.score_answer(bad, entry) < 1.0


def test_answer_domain_nonnegative():
    task = IncentiveCompatibleMenu()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(15):
            entry = task.generate_example()
            assert int(entry.answer) >= 0


def test_brute_force_matches_relaxation():
    random.seed(0)
    task = IncentiveCompatibleMenu()
    task.config.set_level(2)
    for _ in range(10):
        entry = task.generate_example()
        m = entry.metadata
        profit, _, _ = _max_profit(m["valuations"], m["caps"], m["weights"])
        assert profit == int(entry.answer)


def test_instance_variety():
    task = IncentiveCompatibleMenu()
    task.config.set_level(0)
    answers = {task.generate_example().answer for _ in range(30)}
    assert len(answers) > 1


def test_both_type_and_dim_counts_appear():
    task = IncentiveCompatibleMenu()
    types_seen = set()
    dims_seen = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(40):
            m = task.generate_example().metadata
            types_seen.add(m["types"])
            dims_seen.add(m["dims"])
    assert types_seen == {2, 3}
    assert dims_seen == {1, 2}


def test_ic_and_ir_respected():
    task = IncentiveCompatibleMenu()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(15):
            m = task.generate_example().metadata
            v, prof, price, w = (
                m["valuations"],
                m["allocation"],
                m["price"],
                m["weights"],
            )
            n = m["types"]
            d = m["dims"]
            for i in range(n):
                for j in range(n):
                    own_val = sum(v[i][k] * prof[i][k] for k in range(d))
                    other_val = sum(v[i][k] * prof[j][k] for k in range(d))
                    # IC: not preferred to deviate
                    assert own_val - price[i] >= other_val - price[j]
                    # voluntary participation
                    assert own_val - price[i] >= 0
                    assert price[i] >= 0


def test_deterministic_under_seed():
    random.seed(123)
    task = IncentiveCompatibleMenu()
    task.config.set_level(3)
    a = [task.generate_example().answer for _ in range(10)]
    random.seed(123)
    task = IncentiveCompatibleMenu()
    task.config.set_level(3)
    b = [task.generate_example().answer for _ in range(10)]
    assert a == b


def test_level_6_generates():
    task = IncentiveCompatibleMenu()
    task.config.set_level(6)
    for _ in range(10):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
