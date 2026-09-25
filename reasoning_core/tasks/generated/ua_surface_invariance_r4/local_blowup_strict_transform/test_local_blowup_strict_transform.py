from reasoning_core.tasks.generated.ua_surface_invariance_r4.local_blowup_strict_transform.local_blowup_strict_transform import (
    LocalBlowupStrictTransform,
    _multiplicity_sequence,
)


def _seq(*args):
    return _multiplicity_sequence(*args)


def test_known_multiplicity_sequences():
    assert _seq(2, 3) == [2]
    assert _seq(2, 5) == [2, 2]
    assert _seq(3, 4) == [3]
    assert _seq(3, 5) == [3, 2]
    assert _seq(4, 7) == [4, 3]
    assert _seq(5, 7) == [5, 2, 2]


def test_reduction_terminal_smooth():
    for a in range(2, 30):
        for b in range(2, 30):
            if a == b or gcd_free(a, b) != 1:
                continue
            seq = _seq(a, b)
            assert seq, "sequence must be non-empty for min>=2 coprime pair"
            x, y = a, b
            for m in seq:
                assert min(x, y) == m >= 2
                if x <= y:
                    y -= x
                else:
                    x -= y
            assert min(x, y) == 1, "sequence must stop exactly when smooth"


def gcd_free(a, b):
    while b:
        a, b = b, a % b
    return a


def test_round_trip_scores_1():
    task = LocalBlowupStrictTransform()
    task.config.set_level(3)
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_levels_differ():
    task = LocalBlowupStrictTransform()
    task.config.set_level(0)
    c0 = task.config.max_exp
    task.config.set_level(6)
    c6 = task.config.max_exp
    assert c6 > c0


def test_diverse_answers_at_level0():
    task = LocalBlowupStrictTransform()
    task.config.set_level(0)
    answers = set()
    for _ in range(200):
        ex = task.generate_example()
        answers.add(ex.answer)
    assert len(answers) >= 3, "must not collapse to a single answer at level 0"


def test_bad_answers_fail():
    task = LocalBlowupStrictTransform()
    task.config.set_level(2)
    ex = task.generate_example()
    assert task.score_answer("", ex) != 1.0
    assert task.score_answer("not an answer", ex) != 1.0
    assert task.score_answer("0", ex) != 1.0
