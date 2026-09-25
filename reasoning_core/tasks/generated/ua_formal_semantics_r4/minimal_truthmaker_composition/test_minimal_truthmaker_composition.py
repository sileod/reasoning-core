import random

from reasoning_core.tasks.generated.ua_formal_semantics_r4.minimal_truthmaker_composition import (
    minimal_truthmaker_composition as m,
)


def _task(level=0):
    return m.MinimalTruthmakerComposition()


def test_generates_and_scores_gold():
    random.seed(1234)
    t = _task()
    t.config.set_level(0)
    for _ in range(30):
        x = t.generate_example()
        assert m.score_answer(x.answer, x) == 1.0


def test_gold_is_no_or_canonical():
    random.seed(7)
    t = _task()
    t.config.set_level(3)
    seen = set()
    for _ in range(60):
        x = t.generate_example()
        seen.add(x.answer)
        assert x.answer == 'NO' or x.answer == 'EMPTY' or all(
            c in 'PQRabcd() ' for c in x.answer)
    assert len(seen) > 1


def test_answer_domain_valid():
    random.seed(99)
    t = _task()
    for level in (0, 6):
        t.config.set_level(level)
        for _ in range(30):
            x = t.generate_example()
            ans = x.answer
            assert ans == 'NO' or ans == 'EMPTY' or ('(' in ans)


def test_all_levels_generate():
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(5):
            t.generate_example()


def test_levels_have_both_labels():
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        labels = set()
        for _ in range(40):
            x = t.generate_example()
            labels.add('no' if x.answer == 'NO' else 'unique')
        assert labels == {'no', 'unique'}, f"level {level} -> {labels}"


def test_junk_not_scored_one():
    t = _task()
    t.config.set_level(0)
    x = t.generate_example()
    assert m.score_answer('garbage', x) == 0.0
    assert m.score_answer('', x) == 0.0


def test_unique_answer_really_supports():
    random.seed(5)
    t = _task()
    for level in (0, 2, 5):
        t.config.set_level(level)
        for _ in range(20):
            x = t.generate_example()
            if x.answer == 'NO':
                assert x.metadata['n_supports'] != 1
                continue
            assert x.metadata['n_supports'] == 1
            assert x.answer == 'EMPTY' or '(' in x.answer

