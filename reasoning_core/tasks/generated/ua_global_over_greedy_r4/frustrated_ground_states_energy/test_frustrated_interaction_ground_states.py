import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from reasoning_core.tasks.generated.ua_global_over_greedy_r4.frustrated_ground_states_energy.frustrated_interaction_ground_states import (
    FrustratedGroundStatesEnergy, FrustratedConfig, _parse_answer,
)


class TestFrustrated:
    def test_answer_roundtrip(self):
        task = FrustratedGroundStatesEnergy()
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0

    def test_levels_change(self):
        c0 = FrustratedConfig()
        c0.set_level(0)
        c6 = FrustratedConfig()
        c6.set_level(6)
        assert c6.num_sites > c0.num_sites

    def test_all_levels_ok(self):
        for level in range(7):
            cfg = FrustratedConfig()
            cfg.set_level(level)
            task = FrustratedGroundStatesEnergy()
            task.config = cfg
            ex = task.generate_entry()
            assert task.score_answer(ex.answer, ex) == 1.0

    def test_junk_rejected(self):
        task = FrustratedGroundStatesEnergy()
        ex = task.generate_example()
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("abc", ex) < 1.0

    def test_energy_domain(self):
        for _ in range(30):
            cfg = FrustratedConfig()
            cfg.set_level(random.randrange(7))
            task = FrustratedGroundStatesEnergy()
            task.config = cfg
            ex = task.generate_entry()
            assert isinstance(ex.metadata["energy"], int)


def _brute(instance):
    from itertools import product
    n_sites = instance["n"]
    dom = sorted(instance["domain"])
    use_p = instance.get("pinned_site") is not None
    pv = instance.get("pinned_val")
    minima = None
    for a in product(dom, repeat=n_sites):
        if use_p and a[instance["pinned_site"]] != pv:
            continue
        e = 0
        for s, w in instance["bias"]:
            e += w[a[s] - 1]
        for a2, b2, tbl in instance["pairs"]:
            e += tbl[a[a2] - 1][a[b2] - 1]
        for t, tbl in instance["high"]:
            e += tbl["".join(map(str, (a[i] - 1 for i in t)))]
        if minima is None or e < minima:
            minima = e
    return minima


class TestCorrectness:
    def test_energy_matches_brute(self):
        for _ in range(15):
            cfg = FrustratedConfig()
            cfg.set_level(random.randrange(7))
            task = FrustratedGroundStatesEnergy()
            task.config = cfg
            ex = task.generate_entry()
            assert ex.metadata["energy"] == _brute(ex.metadata)

    def test_no_constant_answer_per_level(self):
        for level in range(7):
            cfg = FrustratedConfig()
            cfg.set_level(level)
            task = FrustratedGroundStatesEnergy()
            task.config = cfg
            answers = {task.generate_entry().answer for _ in range(8)}
            assert len(answers) >= 2, "level {} produced a single answer {}".format(level, answers)

