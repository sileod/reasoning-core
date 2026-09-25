from fractions import Fraction

import pytest

from reasoning_core.tasks.generated.ua_state_tracking_r4.strategy_realization_equivalence.strategy_realization_equivalence import (
    StrategyRealizationEquivalence,
)


@pytest.fixture
def task():
    return StrategyRealizationEquivalence()


def test_generate_render_score_roundtrip(task):
    ex = task.generate_example()
    assert ex.prompt
    assert ex.answer == ex.metadata["gold"]
    assert task.score_answer(ex.answer, ex) == 1


def test_answer_is_possible_fraction(task):
    for _ in range(50):
        ex = task.generate_example()
        frac = Fraction(ex.answer)
        assert frac.denominator > 0
        assert 0 <= frac <= 1


def test_wrong_and_junk_score_zero(task):
    ex = task.generate_example()
    assert task.score_answer('7/13', ex) < 1 or Fraction(ex.answer) == Fraction(7, 13)
    assert task.score_answer('', ex) == 0
    assert task.score_answer('abc/xyz', ex) == 0
    assert task.score_answer('1/0', ex) == 0
    assert task.score_answer('not a fraction', ex) == 0


def test_right_commitment_yields_zero(task):
    from reasoning_core.template import Entry
    entry = Entry(metadata={"n": 3, "nodes": ["chance 1/2", "decision right", "chance 1/2"], "gold": "0"}, answer="0")
    assert task.score_answer("0", entry) == 1
    assert task.score_answer("1/2", entry) == 0


def test_all_levels_generate(task):
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1


def test_difficulty_changes_config(task):
    c0 = task.config.to_dict()
    task.config.set_level(3)
    assert task.config.to_dict() != c0


def test_zero_rate_stays_mixed_at_every_level():
    for level in range(7):
        task = StrategyRealizationEquivalence()
        zeros = 0
        n = 80
        for _ in range(n):
            if Fraction(task.generate_example(level=level).answer) == 0:
                zeros += 1
        assert zeros < 0.5 * n


def test_metadata_json_roundtrip(task):
    import json
    ex = task.generate_example()
    md = json.loads(json.dumps(dict(ex.metadata)))
    assert md["nodes"] == ex.metadata["nodes"]
    assert md["gold"] == ex.answer


def test_non_reduced_gold_not_required(task):
    ex = task.generate_example()
    frac = Fraction(ex.answer)
    if frac.denominator > 1 and ex.answer != "0":
        doubled = f"{frac.numerator * 2}/{frac.denominator * 2}"
        assert task.score_answer(doubled, ex) == 1
