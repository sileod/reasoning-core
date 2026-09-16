from reasoning_core.tasks.generated.k3_dynamic_structures_r1.segment_tree_lazy_propagation.segment_tree_lazy_propagation import (
    SegmentTreeLazyPropagation,
)


def test_roundtrip():
    task = SegmentTreeLazyPropagation()
    task.config.set_level(0)
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_and_empty():
    task = SegmentTreeLazyPropagation()
    task.config.set_level(0)
    e = task.generate_example()
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("not an answer", e) == 0.0


def test_wrong_answer():
    task = SegmentTreeLazyPropagation()
    task.config.set_level(0)
    e = task.generate_example()
    parts = e.answer.split(";")
    if len(parts) == 1:
        wrong = str(int(parts[0]) + 1)
        assert task.score_answer(wrong, e) == 0.0


def test_answer_matches_trace():
    task = SegmentTreeLazyPropagation()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(30):
            e = task.generate_example()
            md = e.metadata
            arr = list(md["init"])
            ans = []
            for op in md["ops"]:
                l, r, typ, val = op
                if typ == "add":
                    for i in range(l - 1, r):
                        arr[i] += val
                elif typ == "set":
                    for i in range(l - 1, r):
                        arr[i] = val
                elif typ == "sum":
                    ans.append(sum(arr[l - 1:r]))
                else:
                    ans.append(min(arr[l - 1:r]))
            assert ans == md["answers"]
            expected = ";".join(str(a) for a in ans)
            assert task.score_answer(expected, e) == 1.0


def test_difficulty():
    task = SegmentTreeLazyPropagation()
    task.config.set_level(0)
    s0 = task.config.size
    task.config.set_level(6)
    s6 = task.config.size
    assert s6 > s0
