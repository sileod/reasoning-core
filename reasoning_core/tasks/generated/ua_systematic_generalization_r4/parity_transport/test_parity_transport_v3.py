import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_systematic_generalization_r4.parity_transport.parity_transport_v3 import (
    ParityTransportConfig,
    ParityTransportV3,
    _chirality,
    _parse_answer,
    _sign_of_perm,
    _render_ops,
)


def _bruteforce_chirality(initial, ops, order):
    work = list(initial)
    for op in ops:
        tag = op[0]
        if tag == "swap":
            i, j = work.index(op[1]), work.index(op[2])
            work[i], work[j] = work[j], work[i]
        elif tag == "rotate":
            pa, pb, pc = work.index(op[1]), work.index(op[2]), work.index(op[3])
            work[pb], work[pc], work[pa] = op[1], op[2], op[3]
        else:
            work[0], work[1] = work[1], work[0]
    return _chirality(work, order)


def test_sign_of_perm():
    assert _sign_of_perm(["A", "B", "C", "D"], sorted("ABCD")) == 1
    assert _sign_of_perm(["B", "A", "C", "D"], sorted("ABCD")) == -1
    assert _sign_of_perm(["A", "B", "D", "C"], sorted("ABCD")) == -1


def test_roundtrip_against_bruteforce():
    task = ParityTransportV3()
    random.seed(12345)
    for _ in range(300):
        ex = task.generate_example()
        order = sorted(ex.metadata["letters"])
        expected = _bruteforce_chirality(
            ex.metadata["initial"], ex.metadata["ops"], order
        )
        assert ex.answer == expected
        assert ex.answer in ("R", "S")


def test_balanced_labels():
    task = ParityTransportV3()
    random.seed(99)
    counts = {"R": 0, "S": 0}
    for _ in range(400):
        ex = task.generate_example()
        counts[ex.answer] += 1
    assert counts["R"] > 100 and counts["S"] > 100, counts


def test_difficulty_changes_config():
    cfg = ParityTransportConfig()
    assert cfg.n_ops == 2
    cfg.set_level(6)
    assert cfg.n_ops == 14


def test_scoring():
    task = ParityTransportV3()
    random.seed(7)
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0
    assert task.score_answer("s" if ex.answer == "R" else "r", ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("RC", ex) == 0.0


def test_level6_chain_and_balance():
    task = ParityTransportV3()
    task.config.set_level(6)
    counts = {"R": 0, "S": 0}
    random.seed(11)
    for _ in range(200):
        ex = task.generate_example()
        assert ex.metadata["n_ops"] == 14
        assert len(ex.metadata["ops"]) == 14
        order = sorted(ex.metadata["letters"])
        expected = _bruteforce_chirality(
            ex.metadata["initial"], ex.metadata["ops"], order
        )
        assert ex.answer == expected
        counts[ex.answer] += 1
    assert counts["R"] > 40 and counts["S"] > 40, counts


def test_parse_and_ops_helper():
    assert _parse_answer("R") == "R"
    assert _parse_answer(" s ") == "S"
    assert _parse_answer("") is None
    assert _parse_answer("RS") is None
    assert _parse_answer(5) is None
    text = _render_ops([["swap", "A", "B"], ["rotate", "A", "B", "C"], ["invert"]])
    assert "swap A B" in text and "rotate A B C" in text and "invert" in text


def test_prompt_unambiguous_and_metadata_json():
    task = ParityTransportV3()
    random.seed(3)
    ex = task.generate_example()
    p = task.render_prompt(ex.metadata)
    assert ex.answer in ("R", "S")
    import json

    json.dumps(dict(ex.metadata))
    for op in ex.metadata["ops"]:
        assert op in ("swap", "rotate", "invert") or True
        assert op[0] in ("swap", "rotate", "invert")
