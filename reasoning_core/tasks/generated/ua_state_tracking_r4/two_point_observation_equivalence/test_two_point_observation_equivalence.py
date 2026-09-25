import random

from reasoning_core.tasks.generated.ua_state_tracking_r4.two_point_observation_equivalence.two_point_observation_equivalence import (
    TwoPointObservationEquivalence,
    _is_flat,
)


def test_yes_uniform_flat():
    t = TwoPointObservationEquivalence()
    t.config.set_level(0)
    v = [3] * 4
    assert _is_flat(2, 2, 5, v) is True


def test_no_checkerboard():
    t = TwoPointObservationEquivalence()
    t.config.set_level(0)
    v = [0, 3, 3, 0]
    assert _is_flat(2, 2, 5, v) is False


def test_generate_balanced_and_valid_across_levels():
    for level in (0, 1, 2, 3, 4, 5, 6):
        t = TwoPointObservationEquivalence()
        t.config.set_level(level)
        answers = []
        for _ in range(20):
            x = t.generate_entry()
            assert t.score_answer(x.answer, x) == 1.0
            assert x.answer in ("yes", "no")
            answers.append(x.answer)
        assert "yes" in answers and "no" in answers


def test_garbage_scores_zero():
    t = TwoPointObservationEquivalence()
    t.config.set_level(0)
    x = t.generate_entry()
    assert t.score_answer("maybe", x) == 0.0
    assert t.score_answer("", x) == 0.0


def test_metadata_json_serializable():
    import json

    t = TwoPointObservationEquivalence()
    t.config.set_level(3)
    x = t.generate_entry()
    json.dumps(x.metadata)


def test_gold_matches_flat_flag():
    random.seed(123)
    t = TwoPointObservationEquivalence()
    t.config.set_level(2)
    x = t.generate_entry()
    gold = _is_flat(x.metadata["rows"], x.metadata["cols"],
                    x.metadata["modulus"], x.metadata["values"])
    assert (x.answer == "yes") == gold
