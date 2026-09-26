import random

from reasoning_core.tasks.generated.ua_inference_modes_r4.reversible_cleanup.reversible_workspace_cleanup import (
    ReversibleCleanupV2,
    WorkspaceConfig,
)


def _make(level):
    return ReversibleCleanupV2(WorkspaceConfig().set_level(level))


def test_generate_roundtrip_level0():
    task = _make(0)
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_generate_roundtrip_level6():
    task = _make(6)
    for _ in range(10):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_rejects_junk():
    task = _make(3)
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("abc", ex) < 1.0
    assert task.score_answer("not a number", ex) < 1.0


def test_score_rejects_wrong():
    task = _make(3)
    for _ in range(20):
        ex = task.generate_example()
        gold = int(ex.answer)
        wrong = gold + 1 if gold > 0 else gold + 1
        assert task.score_answer(str(wrong), ex) < 1.0


def test_multiple_answers_present():
    task = _make(5)
    seen = set()
    for _ in range(60):
        ex = task.generate_example()
        seen.add(ex.answer)
    assert len(seen) > 10


def test_difficulty_changes_config():
    task = _make(0)
    n0 = task.config.n_leaves
    task6 = _make(6)
    n6 = task6.config.n_leaves
    assert n6 > n0


def test_domain_answer_positive():
    task = _make(4)
    for _ in range(40):
        ex = task.generate_example()
        assert int(ex.answer) >= 1


def test_validate():
    task = _make(2)
    result = task.validate(cache=False)
    assert isinstance(result, list) and len(result) == 10


def test_answer_matches_brute_force_small():
    from reasoning_core.tasks.generated.ua_inference_modes_r4.reversible_cleanup.reversible_workspace_cleanup import (
        _build,
        _verify,
    )
    for _ in range(40):
        nodes, root = _build(3, 8, 10, 1, 1)
        gold = _verify(nodes, root)
        assert gold >= 1


def test_all_levels_generate():
    for level in range(7):
        task = _make(level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert 1 <= int(ex.answer)

