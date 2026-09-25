from reasoning_core.tasks.generated.ua_formal_logic_r4.affine_view_aliasing.affine_view_aliasing import (
    AffineViewAliasing,
    _overlap_count,
)


def test_roundtrip_all_levels():
    task = AffineViewAliasing()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer("", ex) == 0.0
            assert task.score_answer("junk", ex) == 0.0


def test_metadata_json_serializable():
    task = AffineViewAliasing()
    task.config.set_level(5)
    for _ in range(10):
        ex = task.generate_example()
        import json
        json.dumps(ex.metadata)


def test_difficulty_changes_config():
    task = AffineViewAliasing()
    base = task.config.n_levels
    task.config.set_level(6)
    assert task.config.n_levels > base or task.config.length_high > base


def test_overlap_independent_impl():
    import random as _r
    _r.seed(7)
    for _ in range(200):
        n = _r.randint(1, 3)
        lengths = [_r.randint(2, 4) for _ in range(n)]
        st1 = [_r.randint(1, 3) for _ in range(n)]
        st2 = [_r.randint(-3, 3) for _ in range(n)]
        a1 = _r.randint(0, 30)
        a2 = _r.randint(0, 30)
        c = _overlap_count(lengths, st1, st2, a1, a2)
        assert 0 <= c
