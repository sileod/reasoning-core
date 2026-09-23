import random

from reasoning_core.tasks.generated.k3_global_from_local_r4.threshold_cascade_fixpoint.threshold_cascade_fixpoint import (
    ThresholdCascadeFixpoint,
    _run_cascade,
)


def test_set_answer_matches_cascade():
    random.seed(12345)
    task = ThresholdCascadeFixpoint()
    for _ in range(200):
        x = task.generate_example()
        md = x.metadata
        if md['mode'] != 'set':
            continue
        neighbors = {int(v): ns for v, ns in md['neighbors'].items()}
        active, _ = _run_cascade(neighbors, md['thresholds'], set(md['seeds']))
        assert set(int(v) for v in x.answer.split(',')) == active
        assert task.score_answer(x.answer, x) == 1.0


def test_round_answer_correct():
    random.seed(999)
    task = ThresholdCascadeFixpoint()
    for _ in range(200):
        x = task.generate_example()
        md = x.metadata
        if md['mode'] != 'round':
            continue
        neighbors = {int(v): ns for v, ns in md['neighbors'].items()}
        _, rounds = _run_cascade(neighbors, md['thresholds'], set(md['seeds']))
        assert int(x.answer) == rounds[md['query']]
        assert md['query'] not in md['seeds']
        assert task.score_answer(x.answer, x) == 1.0


def test_saturate_answer_correct():
    random.seed(7)
    task = ThresholdCascadeFixpoint()
    sizes = {'yes': 0, 'no': 0}
    for _ in range(300):
        x = task.generate_example()
        md = x.metadata
        if md['mode'] != 'saturate':
            continue
        sizes[x.answer] += 1
        neighbors = {int(v): ns for v, ns in md['neighbors'].items()}
        active, _ = _run_cascade(neighbors, md['thresholds'], set(md['seeds']))
        assert (len(active) == md['nodes']) == (x.answer == 'yes')
        assert task.score_answer(x.answer, x) == 1.0
    assert sizes['yes'] > 0 and sizes['no'] > 0


def test_junk_and_wrong_answers():
    random.seed(42)
    task = ThresholdCascadeFixpoint()
    for _ in range(300):
        x = task.generate_example()
        assert task.score_answer("", x) < 1.0
        assert task.score_answer("garbage here", x) < 1.0
        assert task.score_answer("   ", x) < 1.0


def test_saturate_balanced_at_all_levels():
    random.seed(2024)
    task = ThresholdCascadeFixpoint()
    for level in (0, 3, 6):
        task.config.set_level(level)
        counts = {'yes': 0, 'no': 0}
        for _ in range(400):
            x = task.generate_example()
            if x.metadata['mode'] != 'saturate':
                continue
            counts[x.answer] += 1
        total = counts['yes'] + counts['no']
        assert total > 50, (level, counts)
        assert counts['yes'] / total > 0.3, (level, counts)
        assert counts['no'] / total > 0.3, (level, counts)


def test_gold_scoring_exact():
    random.seed(5)
    task = ThresholdCascadeFixpoint()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(200):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_answer_roundtrip_invariants():
    random.seed(31337)
    task = ThresholdCascadeFixpoint()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(200):
            x = task.generate_example()
            md = x.metadata
            neighbors = {int(v): ns for v, ns in md['neighbors'].items()}
            active, rounds = _run_cascade(neighbors, md['thresholds'], set(md['seeds']))
            mode = md['mode']
            if mode == 'set':
                assert set(int(v) for v in x.answer.split(',')) == active
            elif mode == 'round':
                assert int(x.answer) == rounds[md['query']]
                assert md['query'] not in md['seeds']
            else:
                assert (x.answer == 'yes') == (md['saturates'])
                assert (len(active) == md['nodes']) == md['saturates']
