import random

from reasoning_core.tasks.generated.wave12.bgp_best_path.bgp_best_path import (
    BgpBestPath, best_path)


def test_gold_answers_score_one():
    task = BgpBestPath()
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_bad_answers_not_all_one():
    task = BgpBestPath()
    for _ in range(30):
        e = task.generate_example()
        n = len(e.metadata['rows'])
        wrong = [i for i in range(n) if str(i) != e.answer]
        wrong_ans = random.choice(wrong)
        assert task.score_answer(wrong_ans, e) < 1.0


def test_junk_rejected():
    task = BgpBestPath()
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("not a number", e) < 1.0


def test_best_path_respects_localpref():
    rows = [
        {'localpref': 100, 'aspath_len': 5, 'origin': 1, 'med': 10, 'router_id': 10},
        {'localpref': 200, 'aspath_len': 1, 'origin': 0, 'med': 5, 'router_id': 20},
    ]
    assert best_path(rows) == 1


def test_best_path_falls_through_rules():
    # Equal localpref and length -> lower origin wins
    rows = [
        {'localpref': 100, 'aspath_len': 3, 'origin': 2, 'med': 5, 'router_id': 10},
        {'localpref': 100, 'aspath_len': 3, 'origin': 0, 'med': 5, 'router_id': 20},
    ]
    assert best_path(rows) == 1
    # Equal except MED -> lower MED wins (ties to -1 treated as largest)
    rows2 = [
        {'localpref': 100, 'aspath_len': 3, 'origin': 1, 'med': -1, 'router_id': 10},
        {'localpref': 100, 'aspath_len': 3, 'origin': 1, 'med': 20, 'router_id': 20},
    ]
    assert best_path(rows2) == 1
    # Full tie -> lowest router ID
    rows3 = [
        {'localpref': 100, 'aspath_len': 3, 'origin': 1, 'med': 5, 'router_id': 30},
        {'localpref': 100, 'aspath_len': 3, 'origin': 1, 'med': 5, 'router_id': 7},
    ]
    assert best_path(rows3) == 1


def test_difficulty_changes():
    task = BgpBestPath()
    task.config.set_level(0)
    n0 = task.config.n_rows
    task.config.set_level(6)
    n6 = task.config.n_rows
    assert n6 >= n0
