import random

from reasoning_core.tasks.generated.ua_formal_semantics_r4.conventional_implicature_separation.conventional_implicature_separation import (
    ConventionalImplicatureSeparation,
)


def _task_at(level=None, seed=0):
    random.seed(seed)
    t = ConventionalImplicatureSeparation()
    if level is not None:
        t.config.set_level(level)
    return t


def test_full_circle_scores_one():
    t = _task_at()
    x = t.generate_example()
    assert t.score_answer(x.answer, x) == 1.0


def test_gold_scores_one_all_levels():
    for level in range(7):
        t = _task_at(level)
        x = t.generate_example()
        assert t.score_answer(x.answer, x) == 1.0, level


def test_junk_and_empty_score_zero():
    for level in range(7):
        t = _task_at(level)
        x = t.generate_example()
        assert t.score_answer("", x) == 0.0, level
        assert t.score_answer("garbage answer", x) == 0.0, level
        assert t.score_answer(12345, x) == 0.0, level


def test_main_asserted_negation_and_conditional():
    t = _task_at(6, seed=3)
    x = t.generate_example()
    for line in x.answer.split("\n"):
        ctx = line.split(":")[0]
        if ctx in ("negation", "conditional"):
            assert "A: main:" in line, line


def test_attitude_main_varies():
    t = _task_at(6, seed=5)
    a_labels = set()
    for _ in range(40):
        x = t.generate_example()
        for line in x.answer.split("\n"):
            if line.startswith("attitude:"):
                a_labels.add("P: main:" in line)
    assert a_labels == {True, False}


def test_supplements_always_projective():
    for _ in range(30):
        t = _task_at(6, seed=99)
        x = t.generate_example()
        for line in x.answer.split("\n"):
            parts = line.split(";")
            for p in parts[1:]:
                assert p.strip().startswith("P: "), line


def test_summary_literal():
    assert (
        ConventionalImplicatureSeparation.summary
        == "Compose asserted and supplementary content for appositives, expressives, "
        "and parentheticals under negation, conditionals, and attitude embedding; "
        "return each content contribution and its attributed source."
    )


def test_design_choice_verbatim():
    assert (
        ConventionalImplicatureSeparation.design_choice
        == "Use a fixed 3x3 grid of answers: for each of negation, conditional, and "
        "attitude, list the content pieces as a semicolon-separated string, each "
        "prefixed by A (asserted) or P (projective)."
    )
