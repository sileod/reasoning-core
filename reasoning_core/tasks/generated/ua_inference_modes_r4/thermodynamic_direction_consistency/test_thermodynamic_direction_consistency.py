from fractions import Fraction

import reasoning_core.tasks.generated.ua_inference_modes_r4.thermodynamic_direction_consistency.thermodynamic_direction_consistency as m


def test_config_difficulty_changes():
    cfg = m.ThermodynamicDirectionConsistencyConfig()
    base = (cfg.species, cfg.partners, cfg.filler)
    cfg.apply_difficulty(6)
    assert (cfg.species, cfg.partners, cfg.filler) >= base
    assert cfg.species >= cfg.partners + 2


def test_generate_answer_scores():
    task = m.ThermodynamicDirectionConsistency()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_answer_is_verifiable_removal():
    task = m.ThermodynamicDirectionConsistency()
    for _ in range(20):
        x = task.generate_example()
        idx = int(x.answer)
        reactions = [(u, v, Fraction(d)) for (u, v, d) in x.metadata["reactions"]]
        assert m._consistent(reactions, idx) is True


def test_wrong_answers_do_not_score():
    task = m.ThermodynamicDirectionConsistency()
    x = task.generate_example()
    correct = int(x.answer)
    for bad in (correct + 1, -1, "x", ""):
        assert task.score_answer(str(bad), x) < 1.0


def test_metadata_json_serializable():
    import json

    task = m.ThermodynamicDirectionConsistency()
    for _ in range(5):
        x = task.generate_example()
        json.dumps(dict(x.metadata))


def test_exactly_one_removal_at_various_levels():
    for level in (0, 2, 5):
        task = m.ThermodynamicDirectionConsistency()
        task.config.set_level(level)
        for _ in range(10):
            x = task.generate_example()
            reactions = [(u, v, Fraction(d)) for (u, v, d) in x.metadata["reactions"]]
            good = [i for i in range(len(reactions)) if m._consistent(reactions, i)]
            assert len(good) == 1
            assert good[0] == int(x.answer)
