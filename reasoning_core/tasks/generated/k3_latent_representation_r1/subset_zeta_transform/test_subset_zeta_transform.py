def _load():
    from reasoning_core.tasks.generated.k3_latent_representation_r1.subset_zeta_transform import subset_zeta_transform as m
    return m


def test_generate_and_score():
    m = _load()
    task = m.SubsetZetaTransform()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert ex.metadata["mode"] in ("zeta", "mobius")
            assert len(ex.metadata["answers"]) == len(ex.metadata["queries"])
            assert task.score_answer(ex.answer, ex) == 1.0


def test_gold_scores_one():
    m = _load()
    task = m.SubsetZetaTransform()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    m = _load()
    task = m.SubsetZetaTransform()
    ex = task.generate_example()
    assert task.score_answer("", ex) != 1.0
    assert task.score_answer("garbage", ex) != 1.0


def test_both_modes_appear():
    m = _load()
    task = m.SubsetZetaTransform()
    modes = set()
    for _ in range(60):
        modes.add(task.generate_example().metadata["mode"])
    assert modes == {"zeta", "mobius"}


def test_apply_difficulty_changes():
    m = _load()
    cfg = m.SubsetZetaTransformConfig()
    before = (cfg.n, cfg.query_count)
    cfg.set_level(5)
    after = (cfg.n, cfg.query_count)
    assert before != after
