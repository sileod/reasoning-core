import json
import random

from reasoning_core.tasks.generated.k3_state_tracking_r4.prufer_coding import (
    prufer_coding as mod,
)


def _all_trees(n):
    seen = set()
    stack = [[] for _ in range(n)]
    for _ in range(5000):
        seq = [random.randint(1, n) for _ in range(n - 2)]
        edges = mod._prufer_decode(n, seq)
        if edges not in seen:
            seen.add(edges)
    return len(seen), n ** (n - 2)


def test_roundtrip_and_scoring():
    task = mod.PruferCoding()
    for level in range(7):
        task.config.set_level(level)
        answers = set()
        for _ in range(24):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0
            answers.add(entry.answer)
            assert task.score_answer("  " + "  ".join(entry.answer.split()) + " ", entry) == 1.0
            assert mod.PruferCoding.score_answer(None, entry.answer, entry) == 1.0
            for junk in ("", "banana", "1 2 x", "999", None, []):
                assert task.score_answer(junk, entry) == 0.0
            assert "edges" in json.loads(json.dumps(dict(entry.metadata)))
            n = entry.metadata["n"]
            assert len(entry.answer.split()) == n - 2
            assert all(1 <= int(v) <= n for v in entry.answer.split())
            assert len(entry.metadata["edges"]) == n - 1
        assert len(answers) > 1


def test_gold_roundtrip_independent():
    for level in range(7):
        task = mod.PruferCoding()
        task.config.set_level(level)
        for _ in range(30):
            entry = task.generate_entry()
            n = entry.metadata["n"]
            seq = [int(v) for v in entry.answer.split()]
            edges = entry.metadata["edges"]
            assert mod._prufer_decode(n, seq) == frozenset(edges)
            assert mod._prufer_encode(n, edges) == tuple(seq)


def test_canonical_small_examples():
    cases = {
        3: {frozenset(((1, 2), (1, 3))): "1",
            frozenset(((1, 2), (2, 3))): "2",
            frozenset(((1, 3), (2, 3))): "3"},
        4: {frozenset(((1, 2), (2, 3), (2, 4))): "2 2",
            frozenset(((1, 2), (1, 3), (1, 4))): "1 1"},
    }
    for n, table in cases.items():
        for edges, code in table.items():
            assert " ".join(map(str, mod._prufer_encode(n, edges))) == code
            redo = mod._prufer_decode(n, [int(v) for v in code.split()])
            assert redo == frozenset(edges)


def test_difficulty_grows():
    task = mod.PruferCoding()
    sizes = []
    for level in range(7):
        task.config.set_level(level)
        sizes.append(max(e.metadata["n"] for e in (task.generate_example() for _ in range(20))))
    assert sizes == sorted(sizes)


def test_answer_fully_determined_by_prompt():
    task = mod.PruferCoding()
    for _ in range(100):
        entry = task.generate_example()
        same_prompt = task.render_prompt(dict(entry.metadata))
        assert same_prompt == task.render_prompt(entry.metadata)
