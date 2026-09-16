import random

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.tree_pattern_occurrence_count.tree_pattern_occurrence_count import (
    _brute_force,
    _count_embeddings,
    _make_random_tree,
    _make_ordered_pattern,
    _Node,
    TreePatternOccurrenceCount,
    WILDCARD,
    LABELS,
)

random.seed(42)


def test_gold_scores_one():
    task = TreePatternOccurrenceCount()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_fail():
    task = TreePatternOccurrenceCount()
    ex = task.generate_example()
    gold = int(ex.answer)
    assert task.score_answer(str(gold + 1), ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("not a number", ex) == 0.0
    assert task.score_answer(str(gold - 1 if gold > 0 else 1), ex) == 0.0


def test_brute_force_matches_dp():
    for _ in range(60):
        alpha = random.choice([2, 3])
        host = _make_random_tree(random.randint(3, 6), alpha)
        pattern = _make_ordered_pattern(random.randint(2, 4), alpha)
        assert _count_embeddings(host, pattern) == _brute_force(host, pattern)


def test_generation_verifies_count():
    for level in (0, 2, 5):
        task = TreePatternOccurrenceCount()
        for _ in range(10):
            ex = task.generate_example(level=level)
            assert int(ex.answer) >= 0


def test_single_node_pattern():
    host = [_Node("a")]
    pattern = [_Node("a")]
    assert _count_embeddings(host, pattern) == 1
    assert _brute_force(host, pattern) == 1


def test_wildcard_matches_any():
    host = [_Node("a"), _Node("b")]
    host[0].children.append(host[1])
    pattern = [_Node(WILDCARD)]
    # wildcard root matches either host node as an embedding
    assert _count_embeddings(host, pattern) == 2
    assert _brute_force(host, pattern) == 2
