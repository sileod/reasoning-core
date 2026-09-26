import random

from reasoning_core.tasks.generated.ua_counterfactual_r4.phylo_network_reconciliation.phylogenetic_network_reconciliation import (
    build_pair,
    hybrid_number,
    _newick,
    _collect,
    phylo_network_reconciliation,
)


def test_construction_hybrid_matches_r():
    for _ in range(200):
        n = random.choice([6, 8, 10, 12])
        rmax = min(n // 3, 4)
        for _w in range(8):
            r = random.randint(1, rmax)
            pair = build_pair(n, r)
            if pair is None:
                continue
            t1, t2 = pair
            leaves = sorted(_collect(t1))
            assert sorted(_collect(t2)) == leaves
            h = hybrid_number(t1, t2)
            assert h == r, (n, r, h, _newick(t1), _newick(t2))
            break


def test_generate_and_score():
    task = phylo_network_reconciliation()
    task.config.set_level(3)
    random.seed(42)
    seen = set()
    for _ in range(40):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        av = int(entry.answer)
        assert av >= 1
        seen.add(av)
    assert len(seen) >= 2


def test_score_rejects_junk():
    task = phylo_network_reconciliation()
    task.config.set_level(0)
    random.seed(1)
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("garbage", entry) < 1.0
    assert task.score_answer(entry.answer + "  ", entry) == 1.0
    assert task.score_answer(str(int(entry.answer) + 1), entry) < 1.0


def test_all_levels():
    task = phylo_network_reconciliation()
    for level in range(7):
        task.config.set_level(level)
        random.seed(level)
        entry = task.generate_example()
        assert int(entry.answer) >= 1
        assert task.score_answer(entry.answer, entry) == 1.0
