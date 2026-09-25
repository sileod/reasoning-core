import random

from reasoning_core.tasks.generated.ua_verification_repair_r4.counterpoint_dissonance_audit.counterpoint_dissonance_audit import (
    CounterpointDissonanceAudit,
    CONSONANT,
    _first_violation,
)


def test_basic_roundtrip():
    random.seed(1234)
    task = CounterpointDissonanceAudit()
    for _ in range(50):
        x = task.generate_example()
        assert x['answer'] == _first_violation(x['metadata']['events'])
        assert task.score_answer(x.answer, x) == 1.0


def test_gold_scores_one_at_levels():
    random.seed(99)
    for level in (0, 2, 5, 6):
        task = CounterpointDissonanceAudit()
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_junk_and_empty_score_zero():
    random.seed(7)
    task = CounterpointDissonanceAudit()
    task.config.set_level(3)
    x = task.generate_example()
    assert task.score_answer('', x) == 0.0
    assert task.score_answer('garbage', x) == 0.0
    assert task.score_answer(None, x) == 0.0


def test_answer_formats():
    random.seed(5)
    task = CounterpointDissonanceAudit()
    for _ in range(40):
        x = task.generate_example()
        a = x.answer
        assert a == 'OK' or (a.count(':') == 2 and a.rsplit(':', 1)[1] in ('accented', 'unaccented'))


def test_consonant_intervals_never_violate():
    for iv in CONSONANT:
        for accent in ('accented', 'unaccented'):
            for label in ('PLAIN', 'SUS', 'PT', 'NT'):
                token = ':'.join((label, str(iv), accent))
                assert _first_violation([token]) == 'OK', token
