import random

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.quantifier_dependency_strategy.quantifier_dependency_strategy import (
    QuantifierDependencyStrategy,
    _parse_strategy,
    _all_assignments,
    _table_at,
)


def test_roundtrip_all_levels():
    random.seed(1)
    t = QuantifierDependencyStrategy()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(15):
            entry = t.generate_example()
            assert t.score_answer(entry.answer, entry) == 1.0, level


def test_wrong_rejected():
    random.seed(2)
    t = QuantifierDependencyStrategy()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(5):
            entry = t.generate_example()
            assert t.score_answer("", entry) < 1.0
            assert t.score_answer("garbage", entry) < 1.0
            if entry.metadata["winning"]:
                assert t.score_answer("UNIVERSAL", entry) < 1.0


def test_all_families_reached():
    random.seed(3)
    t = QuantifierDependencyStrategy()
    seen = set()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(6):
            seen.add(t.generate_example().metadata["family"])
    assert {"linear", "dependent", "branching", "slashed"} <= seen


def test_both_labels_appear():
    random.seed(4)
    t = QuantifierDependencyStrategy()
    wins, losses = 0, 0
    for _ in range(600):
        t.config.set_level(random.randint(1, 6))
        entry = t.generate_example()
        if entry.metadata["winning"]:
            wins += 1
        else:
            losses += 1
    assert wins > 0 and losses > 0


def test_existential_strategy_satisfies_all_clauses():
    random.seed(5)
    t = QuantifierDependencyStrategy()
    t.config.set_level(5)
    seen_universal = False
    for _ in range(40):
        entry = t.generate_example()
        if not entry.metadata["winning"]:
            seen_universal = True
            continue
        dom = entry.metadata["domain_size"]
        n_univ = entry.metadata["n_universal"]
        n_ex = entry.metadata["n_existential"]
        strat = _parse_strategy(entry.answer, dom, n_univ, n_ex)
        assert strat is not None
        for ua in _all_assignments(dom, n_univ):
            ea = strat[ua]
            for vars_list, table in entry.metadata["clauses"]:
                args = tuple(ua[v] if v >= 0 else ea[-v - 1] for v in vars_list)
                assert _table_at(table, args, dom) == 1
    assert seen_universal
