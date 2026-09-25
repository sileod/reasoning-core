import random

from reasoning_core.tasks.generated.ua_relational_structures_r4.recursive_path_order_comparison.recursive_path_order_comparison import (
    LABELS,
    RecursivePathOrderComparison,
    _compare,
    _gt,
    _render_term,
)


def test_smoke():
    task = RecursivePathOrderComparison()
    for _ in range(50):
        x = task.generate_example()
        assert x.answer in LABELS
        assert x.metadata["answer"] == x.answer
        assert task.score_answer(x.answer, x) == 1.0


def test_ground_truth_reproduced():
    task = RecursivePathOrderComparison()
    for _ in range(50):
        x = task.generate_example()
        a = x.metadata["A"]
        b = x.metadata["B"]
        higher = {}
        for pair in x.metadata["precedence"]:
            u, v = pair.split(" > ")
            higher.setdefault(u, set()).add(v)
        out = _compare(a, b, higher, x.metadata["ext"])
        assert out == x.answer


def test_score_rejects_other_labels():
    task = RecursivePathOrderComparison()
    for _ in range(30):
        x = task.generate_example()
        for lab in LABELS:
            if lab != x.answer:
                assert task.score_answer(lab, x) < 1.0
        assert task.score_answer("", x) < 1.0
        assert task.score_answer("banana", x) < 1.0


def test_irreflexive():
    task = RecursivePathOrderComparison()
    for _ in range(20):
        a = task.generate_entry().metadata["A"]
        assert not _gt(a, a, {}, "lex", {})
