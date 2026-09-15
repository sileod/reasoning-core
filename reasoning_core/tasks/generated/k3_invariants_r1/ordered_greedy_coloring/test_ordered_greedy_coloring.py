import random

from reasoning_core.tasks.generated.k3_invariants_r1.ordered_greedy_coloring.ordered_greedy_coloring import (  # noqa: E501
    OrderedGreedyColoring,
)


def test_gold_scoring_all_levels():
    random.seed(7)
    task = OrderedGreedyColoring()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(5):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_empty_and_junk_do_not_score():
    random.seed(7)
    task = OrderedGreedyColoring()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(3):
            entry = task.generate_example()
            assert task.score_answer("", entry) < 1.0
            assert task.score_answer("garbage", entry) < 1.0


def test_answers_canonical():
    random.seed(7)
    task = OrderedGreedyColoring()
    for _ in range(20):
        entry = task.generate_example()
        out = entry.metadata['output']
        if out == 'assignment':
            assert len(entry.answer.split()) == len(entry.metadata['order'])
        else:
            assert entry.answer.isdigit()


def test_difficulty_changes_config():
    random.seed(7)
    task = OrderedGreedyColoring()
    task.config.set_level(0)
    base_n = task.config.n
    task.config.set_level(6)
    assert task.config.n > base_n


def test_color_matches_reference():
    random.seed(7)
    task = OrderedGreedyColoring()
    for _ in range(10):
        entry = task.generate_example()
        order = entry.metadata['order']
        adj = {int(k): v for k, v in entry.metadata['adjacency'].items()}
        color = {}
        for v in order:
            used = {color[u] for u in adj[v] if u in color}
            c = 1
            while c in used:
                c += 1
            color[v] = c
        out = entry.metadata['output']
        if out == 'color':
            c = color[entry.metadata['query']]
            assert int(entry.answer) == c
        elif out == 'count':
            assert int(entry.answer) == len(set(color.values()))
        else:
            expected = [color[v] for v in range(len(order))]
            assert [int(x) for x in entry.answer.split()] == expected


def test_all_output_modes_reachable():
    random.seed(7)
    task = OrderedGreedyColoring()
    task.config.set_level(6)
    seen = set()
    for _ in range(200):
        seen.add(task.generate_example().metadata['output'])
    assert seen >= {'color', 'count', 'assignment'}


def test_all_families_reachable():
    random.seed(7)
    task = OrderedGreedyColoring()
    seen = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            seen.add(task.generate_example().metadata['family'])
    assert seen >= {'path', 'cycle', 'tree', 'grid'}


def test_colors_one_based():
    random.seed(7)
    task = OrderedGreedyColoring()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_example()
            values = [int(x) for x in entry.answer.split()]
            assert all(v >= 1 for v in values)

