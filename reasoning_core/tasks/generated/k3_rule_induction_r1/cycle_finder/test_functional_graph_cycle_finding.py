import random

from reasoning_core.tasks.generated.k3_rule_induction_r1.cycle_finder.functional_graph_cycle_finding import (
    CycleConfig,
    CycleFinder,
    _simulate,
)


def test_generate_and_score():
    task = CycleFinder()
    task.config.set_level(0)
    for _ in range(50):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_wrong_answers_fail():
    task = CycleFinder()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("0 0 0", entry) == 0.0
    assert task.score_answer("not numbers", entry) == 0.0


def test_simulate_consistency():
    n = 20
    domain = list(range(n))
    # build a map whose in-trees merge into one cycle
    table = {}
    for v in domain:
        table[v] = random.choice(domain)
    for start in domain:
        ep, tail, clen = _simulate(table, start)
        assert ep in domain
        assert tail >= 0
        assert clen >= 1
        # verify entry point indeed cycles with given length
        x = table[ep]
        for _ in range(clen - 1):
            x = table[x]
        assert x == ep


def test_difficulty_changes():
    cfg = CycleConfig()
    base = cfg.domain_size
    cfg.set_level(6)
    assert cfg.domain_size > base


def test_deterministic_seed():
    random.seed(1234)
    t1 = CycleFinder()
    t1.config.set_level(2)
    a = t1.generate_example().metadata
    random.seed(1234)
    t2 = CycleFinder()
    t2.config.set_level(2)
    b = t2.generate_example().metadata
    keys = ["successor_table", "domain", "start", "entry_point", "tail_length", "cycle_length"]
    for k in keys:
        assert a[k] == b[k]
