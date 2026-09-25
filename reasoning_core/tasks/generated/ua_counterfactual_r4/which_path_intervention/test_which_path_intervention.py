from fractions import Fraction

from reasoning_core.tasks.generated.ua_counterfactual_r4.which_path_intervention.which_path_intervention import (
    WhichPathIntervention,
    _parse_fraction,
)


def test_gold_score_roundtrip():
    task = WhichPathIntervention()
    for _ in range(30):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0, e
        assert 0.0 <= Fraction(e.answer) <= 1.0


def test_parse_fraction():
    assert _parse_fraction("3/4") == Fraction(3, 4)
    assert _parse_fraction("3") == Fraction(3, 1)
    assert _parse_fraction(" -1 / 2 ") == Fraction(-1, 2)
    assert _parse_fraction("abc") is None
    assert _parse_fraction("1/0") is None


def test_wrong_and_garbage():
    task = WhichPathIntervention()
    e = task.generate_example()
    gold = Fraction(e.answer)
    wrong = 1 - gold
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("not a fraction", e) < 1.0
    assert task.score_answer(str(wrong), e) < 1.0


def test_metadata_json_serializable():
    import json
    task = WhichPathIntervention()
    e = task.generate_example()
    json.dumps(e.metadata)


def test_levels_vary():
    task = WhichPathIntervention()
    sizes = set()
    for level in (0, 3, 6):
        task.config.set_level(level)
        sizes.add(task.config.n_nodes)
    assert len(sizes) >= 2
