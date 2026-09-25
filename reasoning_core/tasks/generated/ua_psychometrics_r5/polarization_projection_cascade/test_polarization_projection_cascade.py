from fractions import Fraction

from reasoning_core.tasks.generated.ua_psychometrics_r5.polarization_projection_cascade.polarization_projection_cascade import (
    PolarizationProjectionCascade,
    compute_intensity,
    cos2_frac,
    format_fraction,
    parse_fraction,
)


def test_gold_scores_one():
    task = PolarizationProjectionCascade()
    for level in (0, 2, 5, 6):
        for _ in range(30):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0, (level, ex.answer)


def test_garbage_scores_zero():
    task = PolarizationProjectionCascade()
    for level in (0, 3, 6):
        ex = task.generate_example(level=level)
        for bad in ("", "garbage", "1.5", "  ", "0/0", "3;4"):
            assert task.score_answer(bad, ex) == 0.0, (bad, ex.answer)


def test_answer_in_domain():
    task = PolarizationProjectionCascade()
    for level in (0, 3, 6):
        for _ in range(20):
            ex = task.generate_example(level=level)
            got = parse_fraction(ex.answer)
            assert 0 <= got <= 1, (level, ex.answer)
            want = Fraction(ex.metadata["ans_num"], ex.metadata["ans_den"])
            assert got == want, (level, ex.answer)


def test_angles_from_supplied_set():
    task = PolarizationProjectionCascade()
    for level in (0, 6):
        ex = task.generate_example(level=level)
        allowed = set(ex.metadata["angles"])

        def check(node):
            if node[0] == "cascade":
                for a in node[1]:
                    assert a in allowed
            else:
                for child in node[2]:
                    check(child)

        check(ex.metadata["program"])


def test_correctness_recomputed():
    task = PolarizationProjectionCascade()
    for level in (0, 5, 6):
        for _ in range(20):
            ex = task.generate_example(level=level)
            want = compute_intensity(ex.metadata["program"], Fraction(1, 1), None)
            assert parse_fraction(ex.answer) == want, level
            assert format_fraction(want) == ex.answer, ex.answer


def test_blocked_vs_partial():
    task = PolarizationProjectionCascade()
    blocked = compute_intensity(("cascade", [0, 90]), Fraction(1, 1), None)
    partial = compute_intensity(("cascade", [0, 30]), Fraction(1, 1), None)
    assert blocked == 0
    assert 0 < partial < 1


def test_difficulty_changes_config():
    task = PolarizationProjectionCascade()
    task.config.set_level(0)
    a = (task.config.arm_len, task.config.max_depth, task.config.top_arms)
    task.config.set_level(6)
    b = (task.config.arm_len, task.config.max_depth, task.config.top_arms)
    assert a != b
    assert b[1] >= a[1]
    assert b[2] >= a[2]


def test_cos2_lookup():
    assert cos2_frac(0) == Fraction(1)
    assert cos2_frac(30) == Fraction(3, 4)
    assert cos2_frac(60) == Fraction(1, 4)
    assert cos2_frac(90) == Fraction(0)
