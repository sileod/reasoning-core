from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.recursion_tree_cost_analysis.recursion_tree_cost_analysis import (
    RecursionTreeCostAnalysis,
)


def test_gold_answer_scores_1():
    for _ in range(50):
        task = RecursionTreeCostAnalysis()
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_garbage_scores_0():
    task = RecursionTreeCostAnalysis()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0


def test_all_levels_generate():
    for level in range(7):
        config = RecursionTreeCostAnalysis.config_cls()
        config.set_level(level)
        task = RecursionTreeCostAnalysis(config=config)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_matches_manual_total():
    for _ in range(30):
        task = RecursionTreeCostAnalysis()
        ex = task.generate_example()
        manual = 0
        for key, count in ex.metadata["sizes"].items():
            n = int(key.split(":")[1])
            manual += (ex.metadata["work_mult"] * n + ex.metadata["base_cost"]) * count
        assert int(ex.answer) == manual
