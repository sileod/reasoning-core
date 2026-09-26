import random
from math import factorial

from reasoning_core.tasks.generated.k3_inference_modes_r4.linear_extension_count.linear_extension_counting import (
    LinearExtensionCountV1,
    _count_linear_extensions,
    _hook_length_count,
    _transitive_closure,
    _generate_poset,
    _random_tree_cover,
)


def test_chain_count():
    n = 5
    cover = [(i, i + 1) for i in range(n - 1)]
    reach = _transitive_closure(cover, n)
    assert _count_linear_extensions(reach, n) == 1
    assert _hook_length_count(cover, n) == 1


def test_empty_count():
    n = 4
    reach = _transitive_closure([], n)
    assert _count_linear_extensions(reach, n) == factorial(4)


def test_star_count():
    cover = [(0, 1), (0, 2), (0, 3)]
    n = 4
    reach = _transitive_closure(cover, n)
    assert _count_linear_extensions(reach, n) == 6
    assert _hook_length_count(cover, n) == 6


def test_hook_matches_dp_on_random_trees():
    random.seed(7)
    for _ in range(20):
        n = 8
        cover = _random_tree_cover(n)
        reach = _transitive_closure(cover, n)
        assert _count_linear_extensions(reach, n) == _hook_length_count(cover, n)


def test_generate_example_roundtrip():
    task = LinearExtensionCountV1()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0
    assert ex.answer.isdigit()
    assert int(ex.answer) >= 1


def test_generate_all_levels():
    task = LinearExtensionCountV1()
    seen = set()
    for level in range(7):
        ex = task.generate_example(level=level)
        assert int(ex.answer) >= 1
        seen.add(ex.answer)
    assert len(seen) > 1


def test_score_rejects_junk():
    task = LinearExtensionCountV1()
    ex = task.generate_example()
    assert task.score_answer("", ex) != 1.0
    assert task.score_answer("abc", ex) != 1.0
    assert task.score_answer("import fakemodule", ex) != 1.0


def test_generate_poset_terminates():
    random.seed(3)
    for _ in range(10):
        reach = _generate_poset(10, 0.25, 0.7)
        assert _count_linear_extensions(reach, 10) >= 1


def test_difficulty_changes_config():
    task = LinearExtensionCountV1()
    task.generate_example(level=3)
    high = task.config.max_n
    task.config.set_level(0)
    low = task.config.max_n
    assert high > low
