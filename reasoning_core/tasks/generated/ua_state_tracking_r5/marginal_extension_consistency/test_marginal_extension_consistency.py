import os
import random
import sys
from fractions import Fraction

from reasoning_core.template import Entry

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from marginal_extension_consistency import (
    MarginalExtensionConsistency,
    _is_compatible,
    _parse_pair,
    _range,
)


def test_smoke_each_mode():
    random.seed(5)
    t = MarginalExtensionConsistency()
    modes = set()
    for _ in range(40):
        ex = t.generate_example()
        assert isinstance(ex, Entry)
        modes.add(ex.metadata.mode)
        assert t.score_answer(ex.answer, ex) == 1.0
    assert modes == {"compat", "range"}


def test_compat_scoring():
    random.seed(7)
    t = MarginalExtensionConsistency()
    for _ in range(60):
        ex = t.generate_example()
        if ex.metadata.mode != "compat":
            continue
        ab = ex.metadata["ab"]
        bc = ex.metadata["bc"]
        d = ex.metadata["states"]
        fab = [[Fraction(c) for c in row] for row in ab]
        fbc = [[Fraction(c) for c in row] for row in bc]
        assert _is_compatible(fab, fbc) == (ex.answer == "yes")
        assert t.score_answer("yes", ex) == (1.0 if ex.answer == "yes" else 0.0)
        assert t.score_answer("no", ex) == (1.0 if ex.answer == "no" else 0.0)
        assert t.score_answer("maybe", ex) == 0.0
        assert t.score_answer("", ex) == 0.0


def test_compat_labels_balanced():
    random.seed(11)
    t = MarginalExtensionConsistency()
    yes = no = 0
    for _ in range(60):
        ex = t.generate_example()
        if ex.metadata.mode == "compat":
            if ex.answer == "yes":
                yes += 1
            else:
                no += 1
    assert yes > 0 and no > 0


def test_range_scoring_and_domain():
    random.seed(13)
    t = MarginalExtensionConsistency()
    for _ in range(60):
        ex = t.generate_example()
        if ex.metadata.mode != "range":
            continue
        lo, hi = _parse_pair(ex.answer)
        assert lo == Fraction(ex.metadata["lo"]) and hi == Fraction(ex.metadata["hi"])
        assert 0 <= lo <= hi <= 1
        assert t.score_answer(ex.answer, ex) == 1.0
        assert t.score_answer(f"{hi} {lo}", ex) == 0.0
        assert t.score_answer("0.5 0.7", ex) == 0.0
        assert t.score_answer("2 3", ex) == 0.0
        assert t.score_answer("", ex) == 0.0


def test_range_matches_gold_definition():
    random.seed(19)
    t = MarginalExtensionConsistency()
    checked = 0
    for _ in range(60):
        ex = t.generate_example()
        if ex.metadata.mode != "range":
            continue
        d = ex.metadata["states"]
        ab = [[Fraction(c) for c in row] for row in ex.metadata["ab"]]
        bc = [[Fraction(c) for c in row] for row in ex.metadata["bc"]]
        lo, hi = _range(ab, bc, ex.metadata["x"], ex.metadata["z"])
        assert (lo, hi) == (Fraction(ex.metadata["lo"]), Fraction(ex.metadata["hi"]))
        checked += 1
    assert checked > 0


def test_all_levels():
    random.seed(23)
    t = MarginalExtensionConsistency()
    for level in range(7):
        t.config.set_level(level)
        ex = t.generate_example()
        assert t.score_answer(ex.answer, ex) == 1.0
        assert ex.metadata["states"] == 2 + level
