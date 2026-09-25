import random
from itertools import permutations

from reasoning_core.tasks.generated.ua_state_tracking_r4.collision_free_moment_extraction.moment_extraction import (
    CollisionFreeMomentExtraction,
    _enum_sum,
    _partition_sum,
    _moments_from_records,
)


def test_generate_and_score():
    task = CollisionFreeMomentExtraction()
    for _ in range(20):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_partition_equals_enumeration():
    task = CollisionFreeMomentExtraction()
    for _ in range(40):
        entry = task.generate_example()
        m = entry.metadata
        attrs = tuple(m["attrs"])
        records = [tuple(r) for r in m["records"]]
        moments = _moments_from_records(records, attrs)
        total_part = _partition_sum(len(attrs), moments)
        total_enum = _enum_sum(records, attrs)
        assert total_part == total_enum == m["collision_free"]


def test_collision_free_differs_from_naive():
    # The collision-free sum and the naive all-record product are equal only
    # when the dropped collision term is exactly 0; the generator must produce
    # both equal and unequal instances across levels on average.
    task = CollisionFreeMomentExtraction()
    unequal = 0
    for _ in range(60):
        entry = task.generate_example()
        m = entry.metadata
        attrs = tuple(m["attrs"])
        records = [tuple(r) for r in m["records"]]
        naive = 1
        for col in range(len(attrs)):
            naive *= sum(r[col] ** attrs[col] for r in records)
        if m["collision_free"] != naive:
            unequal += 1
    assert unequal > 0


def test_gold_not_on_surface():
    import re
    task = CollisionFreeMomentExtraction()
    for _ in range(20):
        entry = task.generate_example()
        m = entry.metadata
        moment_vals = set(mi["value"] for mi in m["moments"])
        assert m["collision_free"] not in moment_vals
        prompt = task.render_prompt(m)
        surface_numbers = {
            int(tok) for tok in re.findall(r"-?\d+", prompt) if tok != ""
        }
        assert m["collision_free"] not in surface_numbers


def test_wrong_and_junk_score_low():
    task = CollisionFreeMomentExtraction()
    entry = task.generate_example()
    target = m0 = entry.metadata["collision_free"]
    assert task.score_answer(str(target + 1), entry) == 0.0
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("abc", entry) == 0.0
    assert task.score_answer("1.5", entry) == 0.0


def test_provides_equivalent_gold():
    # Recompute via brute force directly from the collision-free definition.
    task = CollisionFreeMomentExtraction()
    for _ in range(20):
        entry = task.generate_example()
        m = entry.metadata
        attrs = tuple(m["attrs"])
        records = [tuple(r) for r in m["records"]]
        total = 0
        for perm in permutations(range(len(records)), len(attrs)):
            t = 1
            for col, rec in enumerate(perm):
                t *= records[rec][col] ** attrs[col]
            total += t
        assert total == m["collision_free"]


def test_all_levels_generate_variety():
    task = CollisionFreeMomentExtraction()
    seen_answers = set()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert len(entry.metadata["attrs"]) == entry.metadata["k"]
        seen_answers.add(entry.answer)
    assert len(seen_answers) >= 5


def test_difficulty_is_monotonic():
    task = CollisionFreeMomentExtraction()
    max_k = max_emax = 0
    for level in range(7):
        task.config.set_level(level)
        k = task.config.k
        emax = task.config.emax
        assert k >= max_k
        assert emax >= max_emax
        max_k, max_emax = k, emax
    assert max_k == 4
    assert max_emax == 3


def test_partition_identity_all_levels():
    # The collision-free sum reproduced by the partition formula (what the
    # prompt inputs imply) always equals direct enumeration at every level.
    task = CollisionFreeMomentExtraction()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_example()
            m = entry.metadata
            attrs = tuple(m["attrs"])
            records = [tuple(r) for r in m["records"]]
            moments = _moments_from_records(records, attrs)
            total = _partition_sum(len(attrs), moments)
            assert total == m["collision_free"]


def test_high_level_has_many_moments():
    task = CollisionFreeMomentExtraction()
    task.config.set_level(6)
    entry = task.generate_example()
    assert len(entry.metadata["moments"]) == 15


def test_recompute_gold_from_stated_moments():
    # A solver having only the stated aggregates (not raw records) can still
    # recover the collision-free sum via the partition formula.
    task = CollisionFreeMomentExtraction()
    for _ in range(20):
        entry = task.generate_example()
        m = entry.metadata
        k = m["k"]
        moments = {}
        for mi in m["moments"]:
            moments[tuple(mi["subset"])] = mi["value"]
        total = _partition_sum(k, moments)
        assert total == m["collision_free"]
