import random

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.question_partition_equivalence.question_partition_equivalence import (
    QuestionPartitionEquivalence,
    _partition,
)


def _make(level=0):
    t = QuestionPartitionEquivalence(level=level)
    return t


def test_generation_and_scoring():
    for lvl in (0, 3, 6):
        t = _make(lvl)
        for _ in range(30):
            ex = t.generate_example()
            assert ex.prompt
            assert ex.answer in ('yes', 'no')
            assert ex.metadata['label'] == ex.answer
            assert t.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_score_zero():
    t = _make(0)
    ex = t.generate_example()
    wrong = 'yes' if ex.answer == 'no' else 'no'
    assert t.score_answer(wrong, ex) == 0.0
    assert t.score_answer('', ex) == 0.0
    assert t.score_answer('maybe', ex) == 0.0
    assert t.score_answer('import x', ex) == 0.0


def test_label_balance():
    counts = {'yes': 0, 'no': 0}
    t = _make(2)
    for _ in range(100):
        counts[t.generate_example().answer] += 1
    assert 0.3 < counts['yes'] / 100 < 0.7


def test_partition_consistency():
    t = _make(3)
    for _ in range(40):
        ex = t.generate_example()
        worlds = ex.metadata['worlds']
        p1 = _partition(ex.metadata['q1_spec'], worlds)
        p2 = _partition(ex.metadata['q2_spec'], worlds)
        assert (ex.answer == 'yes') == (p1 == p2)


def test_examples_vary():
    t = _make(1)
    prompts = {t.generate_example().prompt for _ in range(20)}
    assert len(prompts) > 5


def test_const_vs_alt_equivalence():
    worlds = [3, 7, 8, 12]
    q1 = {'type': 'const'}
    q2 = {'type': 'alt', 'alts': [(3,), (7,), (8,), (12,)]}
    assert _partition(q1, worlds) == _partition(q2, worlds)


def test_nonconstant():
    from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.question_partition_equivalence.question_partition_equivalence import (
        _nonconstant_pred,
        _eval,
    )
    random.seed(1)
    for _ in range(20):
        p = _nonconstant_pred(30, 2)
        vals = {_eval(p, v) for v in range(31)}
        assert len(vals) == 2
