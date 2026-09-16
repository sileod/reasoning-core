import random

from reasoning_core.template import Task

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.bottom_up_tree_automaton_run.bottom_up_tree_automaton_run import (
    BottomUpTreeAutomatonRun,
)


def test_score_gold():
    random.seed(1339177894)
    task = BottomUpTreeAutomatonRun()
    for level in (0, 2, 5):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    random.seed(5)
    task = BottomUpTreeAutomatonRun()
    for level in (0, 2, 5):
        ex = task.generate_example(level=level)
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("garbage", ex) < 1.0
        assert task.score_answer("42", ex) < 1.0


def test_level_up_changes_config():
    task = BottomUpTreeAutomatonRun()
    c0 = dict(task.config.to_dict())
    task.config.set_level(6)
    c6 = dict(task.config.to_dict())
    assert c0["tree_depth"] < c6["tree_depth"]


def test_acceptance_balanced():
    random.seed(7)
    task = BottomUpTreeAutomatonRun()
    counts = {"yes": 0, "no": 0}
    for _ in range(80):
        ex = task.generate_example(level=5)
        counts[ex.metadata["accepted"]] += 1
    assert counts["no"] >= 10
    assert counts["yes"] >= 10


def test_all_levels_generate():
    random.seed(3)
    task = BottomUpTreeAutomatonRun()
    for level in range(0, 7):
        for _ in range(10):
            ex = task.generate_example(level=level)


def test_domain_bounds():
    random.seed(17)
    task = BottomUpTreeAutomatonRun()
    for level in (0, 3, 6):
        for _ in range(20):
            ex = task.generate_example(level=level)
            ns = ex.metadata["num_states"]
            assert 0 <= len(ex.metadata["root_states"]) <= ns
            assert ex.metadata["accepted"] == ("yes" if ex.metadata["root_states"] else "no")


def test_answer_format_roundtrip():
    random.seed(11)
    task = BottomUpTreeAutomatonRun()
    for level in (0, 3, 6):
        ex = task.generate_example(level=level)
        root = ex.metadata["root_states"]
        acc = ex.metadata["accepted"]
        expected = "{" + (" ".join(f"s{x}" for x in sorted(root)) if root else "") + "}|" + acc
        assert ex.answer == expected
