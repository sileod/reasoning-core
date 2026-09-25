import random
import re

from reasoning_core.tasks.generated.ua_formal_logic_r4.layered_interval_exposure.layered_interval_exposure import (
    LayeredIntervalExposure as Task,
)


def _parse_answer(answer):
    if answer == "none":
        return []
    spans = []
    for tok in answer.split(";"):
        m = re.match(r"\[(\d+),(\d+)\]:(\d+)", tok)
        spans.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    return spans


def _brute_visible(metadata):
    span = metadata["span"]
    layers = list(metadata["layers"])
    for op in metadata["ops"]:
        if op["kind"] == "remove":
            for l in layers:
                if l["id"] == op["id"]:
                    layers.remove(l)
                    break
        elif op["kind"] == "activate":
            for l in metadata["layers"]:
                if l["id"] == op["id"]:
                    if l not in layers:
                        layers.append(l)
                    break
        else:
            for l in layers:
                if l["id"] == op["id"]:
                    l["prio"] = op["prio"]
                    break
    visible = [None] * span
    for pos in range(span):
        best = None
        bp = None
        for l in layers:
            if l["lo"] <= pos <= l["hi"]:
                if best is None or l["prio"] > bp:
                    best = l["id"]
                    bp = l["prio"]
        visible[pos] = best
    return visible


def test_brute_force_roundtrip():
    random.seed(0)
    for _ in range(50):
        t = Task()
        entry = t.generate_entry()
        assert entry.answer == entry.metadata["answer"]
        parsed = _parse_answer(entry.answer)
        ref = _brute_visible(entry.metadata)
        expected_spans = []
        i = 0
        n = len(ref)
        while i < n:
            if ref[i] is None:
                i += 1
                continue
            j = i
            while j + 1 < n and ref[j + 1] == ref[i]:
                j += 1
            expected_spans.append((i, j, ref[i]))
            i = j + 1
        assert parsed == expected_spans, (entry.answer, expected_spans)


def test_scoring():
    random.seed(1)
    t = Task()
    entry = t.generate_entry()
    assert t.score_answer(entry.answer, entry) == 1.0
    assert t.score_answer("none", entry) < 1.0
    assert t.score_answer("", entry) < 1.0
    assert t.score_answer("junk", entry) < 1.0


def test_levels():
    for level in (0, 2, 5):
        conf = Task().config_cls()
        conf.set_level(level)
        t = Task(config=conf)
        entry = t.generate_entry()
        assert t.score_answer(entry.answer, entry) == 1.0
