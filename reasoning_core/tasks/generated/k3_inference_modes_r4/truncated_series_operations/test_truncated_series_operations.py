import random
from fractions import Fraction

from reasoning_core.tasks.generated.k3_inference_modes_r4.truncated_series_operations.truncated_series_operations import (
    TruncatedSeriesOperations,
    _comp,
    _inv,
    _mul,
    _rev,
)


def test_validate_round_trip():
    t = TruncatedSeriesOperations()
    x = t.generate_example()
    assert t.score_answer(x.answer, x) == 1.0


def test_operations_smoke():
    n = 4
    a = [Fraction(1), Fraction(1, 2), Fraction(-1, 3), Fraction(1)]
    b = [Fraction(0), Fraction(2), Fraction(1, 2), Fraction(-1)]
    assert _mul(a, b, n)
    assert _comp(a, b, n)
    inv = _inv(a, n)
    assert _mul(a, inv, n) == [Fraction(int(i == 0)) for i in range(n)]
    f = [Fraction(0), Fraction(1), Fraction(1), Fraction(1)]
    g = _rev(f, n)
    assert _comp(f, g, n) == [Fraction(int(i == 1)) for i in range(n)]


def test_identity_verification_in_entries():
    t = TruncatedSeriesOperations()
    for _ in range(60):
        x = t.generate_example()
        meta = x["metadata"]
        n = meta["order"]
        F = [Fraction(c) for c in meta["F"]]
        op = meta["operation"]
        result = None
        if op == "multiply":
            G = [Fraction(c) for c in meta["G"]]
            result = _mul(F, G, n)
        elif op == "compose":
            G = [Fraction(c) for c in meta["G"]]
            result = _comp(F, G, n)
        elif op == "invert":
            result = _inv(F, n)
        else:
            result = _rev(F, n)
        if meta["output"] == "list":
            from reasoning_core.tasks.generated.k3_inference_modes_r4.truncated_series_operations.truncated_series_operations import (
                _parse_list,
            )
            assert _parse_list(x["answer"]) == tuple(result)
        else:
            idx = None
            for i, v in enumerate(result):
                if v != 0:
                    idx = i
                    break
            assert str(idx) in x["answer"]


def test_difficulty_changes_config():
    t = TruncatedSeriesOperations()
    t.config.set_level(6)
    assert t.config.order >= TruncatedSeriesOperations().config.order


def test_score_rejects_junk():
    t = TruncatedSeriesOperations()
    x = t.generate_example()
    for junk in ("", "import fakemodule", "asdf", "999/1"):
        assert t.score_answer(junk, x) < 1.0


def test_reproducible_under_seed():
    random.seed(12345)
    t = TruncatedSeriesOperations()
    a = t.generate_example().answer
    random.seed(12345)
    t2 = TruncatedSeriesOperations()
    b = t2.generate_example().answer
    assert a == b
