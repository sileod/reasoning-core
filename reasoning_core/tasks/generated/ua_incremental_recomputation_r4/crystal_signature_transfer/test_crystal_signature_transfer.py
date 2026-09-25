import random
import json

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.\
    crystal_signature_transfer.crystal_signature_transfer import (
        CrystalSignatureTransfer,
        CrystalSignatureConfig,
        _raise_chain,
        _signature,
        _verify,
        _parse_coords,
    )


def _task(level=0):
    return CrystalSignatureTransfer(config=CrystalSignatureConfig())


def test_generate_and_score():
    t = _task()
    for _ in range(30):
        ex = t.generate_example()
        assert isinstance(ex, Entry)
        assert t.score_answer(ex.answer, ex) == 1
        json.dumps(dict(ex.metadata))


def test_levels_all_work():
    for level in range(7):
        t = _task()
        for _ in range(10):
            ex = t.generate_example(level=level)
            assert t.score_answer(ex.answer, ex) == 1


def test_answer_matches_chain():
    t = _task()
    for _ in range(20):
        ex = t.generate_entry()
        positions = ex.metadata["changed_coords"]
        expected = []
        for r, c in positions:
            expected.append([r, c])
        assert ex.answer == str(expected)


def test_null_move_empty():
    # a fully matched word must yield empty answer
    t = _task()
    word = [1, 2]
    final, positions = _raise_chain(word, 1)
    assert positions == ()
    _verify(word, 1, final, positions)


def test_known_chain():
    # 2x3 grid reading word [1,2,1,1,3,1] with i=1 -> positions 5 then 2 -> cells [[0,2],[1,2]]
    word = [1, 2, 1, 1, 3, 1]
    final, positions = _raise_chain(word, 1)
    assert list(positions) == [5, 2]
    wd, h = 3, 2
    coords = [[h - 1 - (p // wd), p % wd] for p in positions]
    assert coords == [[0, 2], [1, 2]]


def test_parse_coords():
    assert _parse_coords("[[1, 1], [0, 1]]") == [[1, 1], [0, 1]]
    assert _parse_coords("[]") == []
    assert _parse_coords("garbage") is None
    assert _parse_coords("[1, 2]") is None
    assert _parse_coords("[[a, b]]") is None


def test_score_rejects_wrong():
    t = _task()
    ex = t.generate_entry()
    # a swapped coordinate order should not score 1 unless coords match exactly
    wrong = list(reversed(ex.metadata["changed_coords"]))
    e = Entry(metadata={"changed_coords": ex.metadata["changed_coords"]}, answer=str(wrong))
    if ex.metadata["changed_coords"] != wrong:
        assert t.score_answer(str(wrong), e) != 1


def test_scorer_robust_to_garbage():
    t = _task()
    ex = t.generate_entry()
    for junk in ["", "import fakemodule", "[[1]]", "None", "123", "[['a','b']]"]:
        val = t.score_answer(junk, ex)
        assert val < 1
