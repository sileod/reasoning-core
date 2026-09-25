import importlib.util
import pathlib
from fractions import Fraction

import pytest

_mod_path = pathlib.Path(__file__).with_name("conditional_coverage_audit.py")
_spec = importlib.util.spec_from_file_location("conditional_coverage_audit_trial", _mod_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TaskCls = _mod.ConditionalCoverageAudit


def _make():
    return TaskCls()


def _recompute(entry):
    a = entry.metadata["advertised_coverage_pct"]
    fracs = []
    failing = []
    for idx, (truths, sets) in enumerate(
            zip(entry.metadata["strata_truth"], entry.metadata["strata_sets"]), start=1):
        covered = sum(
            1 for truth, s in zip(truths, sets)
            if truth in _parse_set(s)
        )
        size = len(truths)
        cov = Fraction(covered, size)
        fracs.append(cov)
        if cov < Fraction(a, 100):
            failing.append(idx)
    return fracs, failing


def _parse_set(s):
    return {int(x) for x in s.strip("{}").split(",") if x != ""}


def test_generate_gold_consistent():
    task = _make()
    entry = task.generate_example()
    assert _mod._parse_answer(entry.answer) is not None
    gold_fracs, gold_failing = _mod._parse_answer(entry.answer)
    exp_fracs, exp_failing = _recompute(entry)
    assert gold_fracs == exp_fracs
    assert gold_failing == exp_failing


def test_score_gold_is_one():
    task = _make()
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1.0


def test_score_junk_is_less_than_one():
    task = _make()
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("junk", entry) < 1.0
    assert task.score_answer("coverage: [3]; failing: [1]", entry) < 1.0


def test_equivalence_fraction_reduction():
    task = _make()
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1.0


def test_all_levels_valid():
    task = _make()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(5):
            entry = task.generate_example()
            parsed = _mod._parse_answer(entry.answer)
            assert parsed is not None
            assert all(0 <= f <= 1 for f in parsed[0])
            assert all(i >= 1 for i in parsed[1])


def test_wrong_answer_not_one():
    task = _make()
    entry = task.generate_example()
    gold_fracs, gold_failing = _mod._parse_answer(entry.answer)
    if gold_failing:
        wrong_failing = "coverage: [" + ", ".join(str(f) for f in gold_fracs) + "]; failing: []"
        assert task.score_answer(wrong_failing, entry) < 1.0
    wrong_frac = "coverage: [" + ", ".join("0" if f != 0 else "1" for f in gold_fracs) + \
                 "]; failing: [" + ", ".join(str(i) for i in gold_failing) + "]"
    assert task.score_answer(wrong_frac, entry) < 1.0


def test_domain_covered_counts():
    task = _make()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_example()
            for c, n in zip(entry.metadata["covered_counts"], entry.metadata["sizes"]):
                assert 0 <= c <= n
