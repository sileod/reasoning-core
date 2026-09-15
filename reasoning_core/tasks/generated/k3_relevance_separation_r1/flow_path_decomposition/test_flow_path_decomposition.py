import random

from reasoning_core.tasks.generated.k3_relevance_separation_r1.flow_path_decomposition.flow_path_decomposition import (
    FlowPathDecomposition,
    FlowPathConfig,
    _decompose,
    _render,
)


def _valid_answer(answer):
    if not answer or ";" not in answer and ":1" not in answer:
        pass
    for part in answer.split("; "):
        path, _, val = part.rpartition(":")
        assert path and val.isdigit(), f"bad path part {part!r}"
        labels = path.split(">")
        assert all(x.isdigit() for x in labels), f"bad label in {path!r}"
        assert len(labels) >= 2, "path must have at least one edge"


def test_gold_scores_and_format():
    task = FlowPathDecomposition()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1
            _valid_answer(ex.answer)


def test_decompose_reproduces_flow():
    flow = {(0, 1): 1, (1, 3): 1, (0, 2): 1, (2, 3): 1}
    paths = _decompose(flow, [0], [3])
    check = {}
    for p, m in paths:
        for a, b in zip(p, p[1:]):
            check[(a, b)] = check.get((a, b), 0) + m
    assert check == flow
    assert _render(paths) == "0>1>3:1; 0>2>3:1"


def test_scoring_rejects_junk():
    task = FlowPathDecomposition()
    ex = task.generate_example()
    for bad in ("", "0>1:1", "not a path", "3>0:2"):
        assert task.score_answer(bad, ex) < 1


def test_render_canonical_order():
    paths = [([0, 1, 3], 2), ([0, 2, 3], 1)]
    assert _render(paths) == "0>1>3:2; 0>2>3:1"


def test_difficulty_changes_config():
    cfg = FlowPathConfig()
    base = (cfg.num_nodes, cfg.flow_units)
    cfg.set_level(3)
    assert (cfg.num_nodes, cfg.flow_units) != base
