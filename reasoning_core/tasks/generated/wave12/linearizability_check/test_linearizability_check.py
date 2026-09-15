import itertools
import random

from reasoning_core.tasks.generated.wave12.linearizability_check.linearizability_check import (
    LinearizabilityCheck,
    _is_linearizable,
)


def _brute(history, intervals):
    n = len(history)
    before = set()
    for i in range(n):
        for j in range(i + 1, n):
            if intervals[i][1] <= intervals[j][0]:
                before.add((i, j))
            elif intervals[j][1] <= intervals[i][0]:
                before.add((j, i))
    for perm in itertools.permutations(range(n)):
        pos = {op: k for k, op in enumerate(perm)}
        if any(pos[a] > pos[b] for a, b in before):
            continue
        value = None
        ok = True
        for opidx in perm:
            op, v = history[opidx]
            if op == "write":
                value = v
            elif value is None:
                ok = False
                break
        if ok:
            return True
    return False


def test_solver_matches_bruteforce():
    random.seed(3)
    for _ in range(300):
        n = random.randint(2, 6)
        history = [
            ("write", random.randint(0, 3))
            if random.random() < 0.5
            else ("read", None)
            for _ in range(n)
        ]
        points = sorted(random.sample(range(0, 2 * n + 2), 2 * n))
        intervals = [(points[2 * i], points[2 * i + 1]) for i in range(n)]
        assert _is_linearizable(history, intervals) == _brute(
            history, intervals
        ), (history, intervals)


def test_linearizable_consistency():
    random.seed(7)
    task = LinearizabilityCheck()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(40):
            e = task.generate_example()
            assert e.answer in ("true", "false")
            expected = _is_linearizable(
                e.metadata["history"], e.metadata["intervals"]
            )
            assert (e.answer == "true") == expected


def test_balance():
    random.seed(11)
    task = LinearizabilityCheck()
    counts = {"true": 0, "false": 0}
    for level in range(7):
        task.config.set_level(level)
        for _ in range(50):
            e = task.generate_example()
            counts[e.answer] += 1
    total = sum(counts.values())
    assert counts["true"] >= total * 0.3
    assert counts["false"] >= total * 0.3
