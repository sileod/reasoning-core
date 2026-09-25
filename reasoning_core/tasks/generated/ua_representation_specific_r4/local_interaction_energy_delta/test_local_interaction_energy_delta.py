from fractions import Fraction

from reasoning_core.tasks.generated.ua_representation_specific_r4.local_interaction_energy_delta.local_interaction_energy_delta import (
    LocalInteractionEnergyDelta, LatticeConfig, _parse_frac,
)


def test_round_trip():
    task = LocalInteractionEnergyDelta()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_gold_scores_one_all_levels():
    task = LocalInteractionEnergyDelta()
    for level in range(7):
        cfg = LatticeConfig()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(15):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_garbage_scores_zero():
    task = LocalInteractionEnergyDelta()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("junk", x) == 0.0
    assert task.score_answer("1/", x) == 0.0
    assert task.score_answer("a/b", x) == 0.0
    assert task.score_answer("0/1", x) == 0.0


def test_wrong_answer_zero():
    task = LocalInteractionEnergyDelta()
    x = task.generate_example()
    num = x.metadata.num
    den = x.metadata.den
    wrong = num + 1
    assert task.score_answer("%d/%d" % (wrong, den), x) == 0.0
    assert task.score_answer("%d/%d" % (num, den + 1), x) == 0.0


def test_difficulty_changes():
    cfg0 = LatticeConfig()
    cfg5 = LatticeConfig()
    cfg0.set_level(0)
    cfg5.set_level(5)
    assert cfg5.n_sites > cfg0.n_sites
    assert cfg5.n_edits > cfg0.n_edits
    assert cfg5.n_pair > cfg0.n_pair


def test_answer_varies():
    task = LocalInteractionEnergyDelta()
    answers = set()
    for _ in range(60):
        x = task.generate_example()
        answers.add(x.answer)
    assert len(answers) >= 20


def test_delta_matches_full_recompute():
    task = LocalInteractionEnergyDelta()
    for _ in range(30):
        x = task.generate_example()
        gold = Fraction(x.metadata.num, x.metadata.den)
        old_total = _parse_frac(x.metadata.old_total)
        new_total = _parse_frac(x.metadata.new_total)
        assert new_total - old_total == gold


def test_no_zero_delta():
    task = LocalInteractionEnergyDelta()
    for _ in range(40):
        x = task.generate_example()
        assert int(x.metadata.num) != 0
