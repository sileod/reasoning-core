import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_counterfactual_r4.constrained_surface_flip_paths.constrained_surface_flip_paths import (
    ConstrainedSurfaceFlipPaths,
)


def test_roundtrip_level0():
    random.seed(1)
    t = ConstrainedSurfaceFlipPaths()
    x = t.generate_example()
    assert t.score_answer(x.answer, x) == 1.0


def test_roundtrip_all_levels():
    random.seed(7)
    t = ConstrainedSurfaceFlipPaths()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(8):
            x = t.generate_example()
            assert t.score_answer(x.answer, x) == 1.0, (level, x.answer)


def test_answer_sequence_matches_gold_edges():
    random.seed(3)
    t = ConstrainedSurfaceFlipPaths()
    t.config.set_level(4)
    x = t.generate_example()
    seq = [tuple(e) for e in x.metadata['gold_edges']]
    ans = x.answer.split(';')
    parsed = [tuple(sorted(int(p) for p in e.split('-'))) for e in ans]
    assert [tuple(sorted(e)) for e in seq] == [tuple(sorted(e)) for e in parsed]


def test_garbage_and_short_answers():
    random.seed(5)
    t = ConstrainedSurfaceFlipPaths()
    for level in (0, 3, 6):
        t.config.set_level(level)
        x = t.generate_example()
        assert t.score_answer('', x) < 1.0
        assert t.score_answer('junk', x) < 1.0
        assert t.score_answer('0-1;9-7;x-y', x) < 1.0
        assert t.score_answer(None, x) < 1.0
