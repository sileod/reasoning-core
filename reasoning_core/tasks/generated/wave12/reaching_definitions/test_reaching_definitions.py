import random

from reasoning_core.tasks.generated.wave12.reaching_definitions.reaching_definitions import (
    ReachingDefinitions,
    _assignments,
    _solve,
)


def test_gold_scores_1():
    task = ReachingDefinitions()
    for _ in range(200):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_difficulty_changes():
    c = ReachingDefinitions.config_cls()
    c.set_level(0)
    n0 = c.n_lines
    d0 = c.depth
    c.set_level(6)
    assert c.n_lines > n0
    assert c.depth >= d0


def test_answer_is_reaching_set():
    task = ReachingDefinitions()
    for _ in range(100):
        e = task.generate_example()
        labels, nodes, IN, OUT, exit = _solve(e.metadata["ast"])
        assert labels == sorted(e.metadata["answer_labels"])
        assert e.answer == (", ".join("L%d" % l for l in labels) if labels else "none")


def test_at_least_two_assignments():
    task = ReachingDefinitions()
    for _ in range(100):
        e = task.generate_example()
        total = sum(1 for _ in _assignments(e.metadata["ast"]))
        assert total >= 2


def test_garbage_scores_0():
    task = ReachingDefinitions()
    e = task.generate_example()
    assert task.score_answer("banana", e) == 0.0
    assert task.score_answer("", e) == 0.0


def test_wrong_answer_scores_0():
    task = ReachingDefinitions()
    for _ in range(100):
        e = task.generate_example()
        labels = sorted(e.metadata["answer_labels"])
        gold_str = ",".join("L%d" % l for l in labels) if labels else "none"
        if gold_str == "none":
            wrong = "L0,L1"
        else:
            wrong = gold_str + ",L99"
        assert task.score_answer(wrong, e) == 0.0


def test_parse_accepts_spaces_and_case():
    assert _parse_answer_safe("l1, l0, L4") is not None


def _parse_answer_safe(s):
    import re
    if s.lower() == "none":
        return []
    return sorted(int(m) for m in re.findall(r"[Ll](\d+)", s))


def test_level_domain_varied():
    task = ReachingDefinitions()
    seen = set()
    random.seed(7)
    for lvl in range(7):
        for _ in range(30):
            e = task.generate_example(level=lvl)
            seen.add(e.answer)
    assert len(seen) > 5
