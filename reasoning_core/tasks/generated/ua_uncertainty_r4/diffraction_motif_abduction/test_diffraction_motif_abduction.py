import random

from reasoning_core.tasks.generated.ua_uncertainty_r4.diffraction_motif_abduction.diffraction_motif_abduction import (
    _autocorr,
    _full_mask,
    _parse_motif,
    _reproduces,
    _weights,
    DiffractionMotifAbduction,
)


def _entry(period, motif, mask):
    from reasoning_core.template import Entry
    return Entry(metadata={'period': period, 'mask': mask, 'weights': motif},
                 answer=motif)


def test_gold_scores_one():
    random.seed(7)
    task = DiffractionMotifAbduction()
    for _ in range(200):
        ex = task.generate_example()
        assert len(ex.answer) == ex.metadata['period']
        assert len(ex.metadata['mask']) == ex.metadata['period']
        assert task.score_answer(ex.answer, ex) == 1.0


def test_translation_acceptance():
    random.seed(7)
    task = DiffractionMotifAbduction()
    ex = task.generate_example()
    motif = ex.answer
    period = ex.metadata['period']
    for shift in range(period):
        rotated = motif[shift:] + motif[:shift]
        assert task.score_answer(rotated, ex) == 1.0


def test_invalid_answers_score_zero():
    random.seed(7)
    task = DiffractionMotifAbduction()
    ex = task.generate_example()
    assert task.score_answer('', ex) == 0.0
    assert task.score_answer('xx', ex) == 0.0
    assert task.score_answer('a' * ex.metadata['period'], ex) == 0.0


def test_non_reproducing_scores_zero():
    task = DiffractionMotifAbduction()
    for _ in range(50):
        ex = task.generate_example()
        period = ex.metadata['period']
        motif = ex.answer
        flipped = '0' if motif[0] != '0' else '+'
        candidate = flipped + motif[1:]
        if task.score_answer(candidate, ex) == 1.0:
            # must actually reproduce the mask if it scored full
            assert _reproduces(_weights(candidate), ex.metadata['mask']) \
                or any(_reproduces(_weights(candidate[s:] + candidate[:s]),
                                   ex.metadata['mask']) for s in range(period))


def test_parse_and_weights():
    assert _weights('+-0') == [1, -1, 0]
    assert _parse_motif(' +-0 ') == '+-0'
    assert _parse_motif('12') is None
    assert _parse_motif('') is None


def test_autocorr_mask_consistency():
    random.seed(3)
    task = DiffractionMotifAbduction()
    for _ in range(200):
        ex = task.generate_example()
        mask = ex.metadata['mask']
        full = _full_mask(_weights(ex.answer))
        for value, observed, truth in zip(_autocorr(_weights(ex.answer)), mask, full):
            if observed == '?':
                continue
            assert observed == truth


def test_observed_positions_balanced():
    random.seed(3)
    task = DiffractionMotifAbduction()
    for _ in range(300):
        ex = task.generate_example()
        observed = [x for x in ex.metadata['mask'] if x != '?']
        assert '1' in observed and '0' in observed


def test_all_levels_generate():
    task = DiffractionMotifAbduction()
    for level in (0, 1, 2, 3, 4, 5, 6):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert ex.metadata['period'] >= 8 + level
