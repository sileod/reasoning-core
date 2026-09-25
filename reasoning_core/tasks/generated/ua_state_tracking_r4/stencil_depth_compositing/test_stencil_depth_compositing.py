import random

from reasoning_core.tasks.generated.ua_state_tracking_r4.stencil_depth_compositing.stencil_depth_compositing import (
    StencilDepthCompositing,
    StencilDepthConfig,
    _simulate,
    _stencil_apply,
)


def test_generate_scores_self():
    random.seed(1277236794)
    t = StencilDepthCompositing()
    for _ in range(30):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_answer_matches_metadata_states():
    random.seed(7)
    t = StencilDepthCompositing()
    for _ in range(40):
        e = t.generate_entry()
        results = _simulate(e.metadata.clear, e.metadata.ops, [tuple(q) for q in e.metadata.queries])
        expected = ';'.join(
            f"{c[0]},{c[1]},{c[2]},{c[3]},{d},{s}" for (c, d, s) in results
        )
        assert e.answer == expected
        for q, (c, d, s) in zip(e.metadata.queries, results):
            for ch in c:
                assert 0 <= ch <= 255
            assert 0 <= d <= 1023
            assert 0 <= s <= 255


def test_per_region_independence():
    random.seed(11)
    t = StencilDepthCompositing()
    for _ in range(20):
        e = t.generate_entry()
        q = [tuple(qq) for qq in e.metadata.queries]
        pixel_results = _simulate(e.metadata.clear, e.metadata.ops, q)
        expected = ';'.join(
            f"{c[0]},{c[1]},{c[2]},{c[3]},{d},{s}" for (c, d, s) in pixel_results
        )
        assert e.answer == expected
        order = {coord: i for i, coord in enumerate(q)}
        for y in range(e.metadata['n']):
            for x in range(e.metadata['n']):
                if (x, y) in order:
                    idx = order[(x, y)]
                    assert pixel_results[idx] == _simulate(e.metadata.clear, e.metadata.ops, [(x, y)])[0]


def test_stencil_ops_semantics():
    s = 5
    assert _stencil_apply(s, 'KEEP', 9) == 5
    assert _stencil_apply(s, 'ZERO', 9) == 0
    assert _stencil_apply(s, 'REPLACE', 9) == 9
    assert _stencil_apply(s, 'INCR', 9) == 6
    assert _stencil_apply(255, 'INCR', 9) == 255
    assert _stencil_apply(s, 'DECR', 9) == 4
    assert _stencil_apply(0, 'DECR', 9) == 0
    assert _stencil_apply(255, 'INCR_WRAP', 9) == 0
    assert _stencil_apply(0, 'DECR_WRAP', 9) == 255
    assert _stencil_apply(5, 'INVERT', 9) == 250


def test_wrong_answers_score_zero():
    random.seed(3)
    t = StencilDepthCompositing()
    e = t.generate_example()
    assert t.score_answer('', e) == 0.0
    assert t.score_answer('garbage', e) == 0.0
    assert t.score_answer('0,0,0,0,0,0;0,0,0,0,0,0', e) == 0.0


def test_difficulty_changes_config():
    cfg = StencilDepthConfig()
    base = (cfg.grid_n, cfg.num_fragments, cfg.num_queries)
    cfg2 = StencilDepthConfig()
    cfg2.apply_difficulty(6)
    assert base != (cfg2.grid_n, cfg2.num_fragments, cfg2.num_queries)
    assert cfg2.num_fragments > cfg.num_fragments


def test_query_domain():
    random.seed(5)
    t = StencilDepthCompositing()
    for level in (0, 2, 5, 6):
        t.config.set_level(level)
        n = t.config.grid_n
        for _ in range(10):
            e = t.generate_entry()
            for (x, y) in e.metadata.queries:
                assert 0 <= x < n and 0 <= y < n
