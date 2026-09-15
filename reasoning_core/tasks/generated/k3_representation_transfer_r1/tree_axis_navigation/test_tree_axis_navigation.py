import random

from reasoning_core.tasks.generated.k3_representation_transfer_r1.tree_axis_navigation.tree_axis_navigation import (
    TreeAxisConfig,
    TreeAxisNavigation,
    _axis,
    _build_tree,
    _parse_list,
)


def _task(level):
    task = TreeAxisNavigation(config=TreeAxisConfig())
    task.config.set_level(level)
    return task


def test_generate_and_score_gold():
    for level in (0, 2, 5, 6):
        task = _task(level)
        ex = task.generate_example()
        assert ex.prompt
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_rejects_wrong_and_garbage():
    task = _task(0)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("[999]", ex) == 0.0
    assert task.score_answer("import os", ex) == 0.0
    assert task.score_answer("not a list", ex) == 0.0


def test_answers_are_valid_lists_of_ints():
    task = _task(5)
    for _ in range(20):
        ex = task.generate_example()
        vals = _parse_list(ex.answer)
        assert len(vals) >= 2
        assert vals == sorted(set(vals))
        assert all(isinstance(v, int) for v in vals)


def test_difficulty_changes_config():
    config = TreeAxisConfig()
    config.set_level(0)
    base_size, base_steps = config.size, config.n_steps
    config.set_level(6)
    assert (config.size, config.n_steps) != (base_size, base_steps)


def test_axis_semantics_small_tree():
    children = {0: [1, 2], 1: [3], 2: [], 3: []}
    parent = {0: None, 1: 0, 2: 0, 3: 1}
    assert _axis(0, "child", children, parent) == [1, 2]
    assert _axis(1, "parent", children, parent) == [0]
    assert _axis(0, "descendant", children, parent) == [1, 3, 2]
    assert _axis(3, "ancestor", children, parent) == [0, 1]
    assert _axis(1, "following-sibling", children, parent) == [2]
    assert _axis(2, "preceding-sibling", children, parent) == [1]


def test_reproducible_under_seed():
    random.seed(7)
    a = _task(3).generate_example().answer
    random.seed(7)
    b = _task(3).generate_example().answer
    assert a == b


def test_build_tree_is_valid_ordered_tree():
    for _ in range(20):
        children, parent, rank = _build_tree(12)
        assert len(children) == 12
        assert parent[0] is None
        for i in range(1, 12):
            assert parent[i] in children
            assert i in children[parent[i]]
        assert len({x for x in rank}) == 12
