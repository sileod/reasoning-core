"""Tests for axis_separable_transitions."""

from reasoning_core.tasks.generated.ua_latent_representation_r4.axis_separable_transitions.axis_separable_transitions import (
    AxisSeparableTransitions,
    _lex_products,
    _from_perm_components,
)

MOD = AxisSeparableTransitions


def test_gold_scores_one():
    task = MOD()
    for _ in range(40):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_answers_are_balanced():
    task = MOD()
    counts = {}
    for _ in range(60):
        x = task.generate_example()
        key = "yes" if x.answer.startswith("yes") else "no"
        counts[key] = counts.get(key, 0) + 1
    assert counts.get("yes", 0) > 0
    assert counts.get("no", 0) > 0


def test_separable_answer_matches_recovery():
    task = MOD()
    for _ in range(30):
        x = task.generate_example()
        if x.answer.startswith("yes"):
            pi = tuple(int(i) for i in x.answer.split()[1:])
            base = x.metadata["base"]
            assert pi is not None
            C = x.metadata["C"]
            R = x.metadata["R"]
            big = {}
            for s in _lex_products(C, R):
                big[s] = _from_perm_components(base, pi, s)
            table = {tuple(s): tuple(t) for s, t in x.metadata["table"]}
            assert big == table


def test_inseparable_no_perm():
    task = MOD()
    for _ in range(30):
        x = task.generate_example()
        if x.answer == "no":
            C = x.metadata["C"]
            R = x.metadata["R"]
            from reasoning_core.tasks.generated.ua_latent_representation_r4.axis_separable_transitions.axis_separable_transitions import (
                _is_separable,
            )
            table = {tuple(s): tuple(t) for s, t in x.metadata["table"]}
            assert _is_separable([], table, C, R) is None


def test_difficulty_changes():
    cfg = MOD.config_cls()
    l0 = cfg.C
    cfg.set_level(6)
    assert cfg.C >= l0
