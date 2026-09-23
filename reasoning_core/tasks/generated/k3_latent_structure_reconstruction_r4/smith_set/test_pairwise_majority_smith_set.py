import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from reasoning_core.template import Entry

from pairwise_majority_smith_set import SmithSetConfig, SmithSetTask, _smith_set


def test_gold_scores():
    random.seed(1)
    task = SmithSetTask()
    for i in range(60):
        task.config.set_level(i % 7)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_difficulty_changes():
    task = SmithSetTask()
    task.config.set_level(0)
    base = task.config.n_candidates
    task.config.set_level(6)
    assert task.config.n_candidates > base


def test_deterministic_across_processes_seed():
    random.seed(123)
    task = SmithSetTask()
    a = task.generate_example()
    random.seed(123)
    task = SmithSetTask()
    b = task.generate_example()
    assert a.answer == b.answer


def test_score_rejects_junk():
    task = SmithSetTask()
    for lvl in range(7):
        task.config.set_level(lvl)
        ex = task.generate_example()
        for bad in ["", "junk", "-5", "1,2,2,2"]:
            assert task.score_answer(bad, ex) < 1.0
        # wrong but plausible
        assert task.score_answer("9,9,9", ex) < 1.0


def test_smith_set_matches_bruteforce():
    random.seed(7)
    for n in range(3, 8):
        for _ in range(30):
            from pairwise_majority_smith_set import _build_tournament
            margin = _build_tournament(n, 3)
            gold = _smith_set(n, margin)
            # brute force: find maximal subset check
            cands = list(range(n))

            def beats(a, b):
                return (a, b) in margin or (b, a) in margin

            def who(a, b):
                return a if (a, b) in margin else b

            adj = {c: set() for c in cands}
            for a in cands:
                for b in cands:
                    if a != b and beats(a, b) and who(a, b) == a:
                        adj[a].add(b)

            def reach(start):
                seen = set(); stack = [start]
                while stack:
                    x = stack.pop()
                    if x in seen: continue
                    seen.add(x); stack.extend(adj[x] - seen)
                return seen

            # Smith set brute: minimal dominant set via not-strictly-dominated
            bf = set()
            for c in cands:
                dominated = False
                rc = reach(c)
                for d in cands:
                    if d == c: continue
                    rd = reach(d)
                    if c in rd and d not in rc:
                        dominated = True; break
                if not dominated:
                    bf.add(c)
            assert gold == bf


def test_json_metadata():
    import json
    random.seed(3)
    task = SmithSetTask()
    ex = task.generate_example()
    json.dumps(ex.metadata)


def test_example_object():
    task = SmithSetTask()
    ex = task.generate_example()
    assert isinstance(ex, Entry)
