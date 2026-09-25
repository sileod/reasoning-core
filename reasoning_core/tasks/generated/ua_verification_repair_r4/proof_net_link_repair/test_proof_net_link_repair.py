import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proof_net_link_repair import (
    ProofNetConfig,
    ProofNetLinkRepair,
    _all_acyclic,
    _min_cyclic_switching,
    _min_repair_pair,
    _swap_endpoints,
    score_answer,
)


def _make():
    return ProofNetLinkRepair()


def test_generate_and_score():
    random.seed(1)
    task = _make()
    for _ in range(40):
        ex = task.generate_example()
        assert score_answer(ex.answer, ex) == 1.0


def test_junk_and_empty_score_below_one():
    random.seed(2)
    task = _make()
    for _ in range(20):
        ex = task.generate_example()
        assert score_answer("", ex) < 1.0
        assert score_answer("garbage", ex) < 1.0
        assert score_answer("swap", ex) < 1.0


def test_both_modes_occur():
    random.seed(3)
    task = _make()
    modes = set()
    for _ in range(60):
        ex = task.generate_example()
        modes.add(ex.metadata["mode"])
    assert modes == {"A", "B"}


def test_gold_answer_consistent_with_internal_solvers():
    random.seed(4)
    task = _make()
    for _ in range(40):
        ex = task.generate_example()
        md = ex.metadata
        par = [tuple(int(x) for x in t) for t in md["par_links"]]
        te = [tuple(int(x) for x in t) for t in md["tensor_edges"]]
        ax = [(l, int(u), int(v)) for (l, u, v) in md["ax_links"]]
        nn = int(md["num_nodes"])
        assert not _all_acyclic(par, te, [(u, v) for (_, u, v) in ax], nn)
        if md["mode"] == "A":
            assert _min_cyclic_switching(par, te, [(u, v) for (_, u, v) in ax], nn) == ex.answer
        else:
            i, j = _min_repair_pair(par, te, ax, nn)
            assert "swap %d %d" % (i, j) == ex.answer


def test_level_changes_config():
    task = _make()
    c0 = ProofNetConfig()
    c0.set_level(0)
    c6 = ProofNetConfig()
    c6.set_level(6)
    assert c6.num_axioms >= c0.num_axioms


def test_mode_b_answer_restores_correctness():
    random.seed(7)
    task = _make()
    for _ in range(40):
        ex = task.generate_example()
        if ex.metadata["mode"] != "B":
            continue
        md = ex.metadata
        par = [tuple(int(x) for x in t) for t in md["par_links"]]
        te = [tuple(int(x) for x in t) for t in md["tensor_edges"]]
        ax = [(l, int(u), int(v)) for (l, u, v) in md["ax_links"]]
        nn = int(md["num_nodes"])
        i, j = (int(x) for x in ex.answer.split()[1:])
        fixed = _swap_endpoints(ax, i, j)
        assert _all_acyclic(par, te, [(u, v) for (_, u, v) in fixed], nn)


def test_generation_at_all_levels():
    random.seed(9)
    task = _make()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            ex = task.generate_example()
            assert score_answer(ex.answer, ex) == 1.0


def test_validate():
    task = _make()
    task.validate()
