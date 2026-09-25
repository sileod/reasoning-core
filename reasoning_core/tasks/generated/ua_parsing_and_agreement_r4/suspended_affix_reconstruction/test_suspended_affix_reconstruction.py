import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_parsing_and_agreement_r4.suspended_affix_reconstruction.suspended_affix_reconstruction import (
    SuspendedAffixConfig,
    SuspendedAffixReconstruction,
)


def test_generate_and_score():
    task = SuspendedAffixReconstruction()
    for _ in range(50):
        x = task.generate_example()
        assert isinstance(x, Entry)
        assert task.score_answer(x.answer, x) == 1.0


def test_wrong_answers_fail():
    task = SuspendedAffixReconstruction()
    for _ in range(30):
        x = task.generate_example()
        assert task.score_answer("", x) == 0.0
        assert task.score_answer("junk", x) == 0.0


def test_difficulty_changes_config():
    cfg = SuspendedAffixConfig()
    base = cfg.max_conjuncts
    cfg.set_level(0)
    l0 = cfg.max_conjuncts
    cfg.set_level(6)
    l6 = cfg.max_conjuncts
    assert l0 == 2
    assert l6 >= 4


def test_deterministic_under_fixed_seed():
    task = SuspendedAffixReconstruction()
    random.seed(1234)
    a = task.generate_example().answer
    random.seed(1234)
    b = task.generate_example().answer
    assert a == b


def test_all_levels_generate():
    task = SuspendedAffixReconstruction()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_answer_format_and_surface():
    task = SuspendedAffixReconstruction()
    for _ in range(40):
        x = task.generate_example()
        assert isinstance(x.answer, str)
        assert " | " in x.answer
        assert x.metadata["stem"] in x.answer
        surface = task.render_prompt(x.metadata)
        mode = x.metadata["mode"]
        stem = x.metadata["stem"]
        for a in x.metadata["affixes"]:
            if mode == "prefix":
                assert a in surface
            else:
                assert a in surface
        assert stem in surface
