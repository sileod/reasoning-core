import random

from reasoning_core.tasks.generated.k3_relational_structures_r1.tree_subset_counting.tree_subset_counting_dp import (
    TreeSubsetCounting,
    _dp,
    _bruteforce,
    _build_tree,
)


def _instance():
    task = TreeSubsetCounting()
    entry = task.generate_example()
    return task, entry


def test_gold_scores_one():
    task, entry = _instance()
    assert task.score_answer(entry.answer, entry) == 1


def test_junk_scores_zero():
    task, entry = _instance()
    assert task.score_answer("", entry) < 1
    assert task.score_answer("reajrjrje9595!", entry) < 1


def test_dp_matches_bruteforce_small():
    random.seed(7)
    for _ in range(40):
        n = random.randint(2, 9)
        children, parents = _build_tree(n)
        for variant in ("independent_set", "matching", "vertex_cover"):
            assert _dp(children, variant, None) == _bruteforce(children, parents, variant)


def test_dp_mod_consistent_with_exact():
    random.seed(11)
    for _ in range(20):
        n = random.randint(2, 9)
        children, parents = _build_tree(n)
        for variant in ("independent_set", "matching", "vertex_cover"):
            exact = _dp(children, variant, None)
            mod = _dp(children, variant, 1000000007)
            assert mod == exact % 1000000007


def test_answer_domain():
    for level in (0, 3, 6):
        task = TreeSubsetCounting()
        for _ in range(10):
            entry = task.generate_example(level=level)
            val = int(entry.answer)
            assert val >= 0
            if entry.metadata["mod"] is not None:
                assert val < entry.metadata["mod"]


def test_prompt_contains_needed_facts():
    task, entry = _instance()
    prompt = task.render_prompt(entry.metadata)
    assert str(entry.metadata["n"]) in prompt
    assert str(entry.metadata["variant"].replace("_", " ")) in prompt
    if entry.metadata["mod"] is not None:
        assert str(entry.metadata["mod"]) in prompt
    assert "dynamic programming" in prompt
