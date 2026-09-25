import random

from reasoning_core.tasks.generated.ua_state_tracking_r4.periodic_density_equivalence.periodic_density_equivalence import (
    PeriodicDensityEquivalence, _site_sum)


def _make(level):
    t = PeriodicDensityEquivalence()
    t.config.set_level(level)
    return t


def test_generate_and_score_all_levels():
    for level in range(7):
        obj = _make(level)
        entry = obj.generate_example()
        assert entry.answer in ("EQ", "NEQ")
        assert obj.score_answer(entry.answer, entry) == 1.0


def test_both_labels_across_levels():
    random.seed(999)
    seen = set()
    for level in (0, 2, 5):
        obj = _make(level)
        for _ in range(30):
            entry = obj.generate_example()
            seen.add(entry.answer)
    assert "EQ" in seen
    assert "NEQ" in seen


def test_equality_consistency():
    for level in range(7):
        obj = _make(level)
        for _ in range(20):
            entry = obj.generate_example()
            n = int(entry.metadata.n)
            fields = entry.metadata.fields
            ta = _eval_expr(entry.metadata.mono_a, fields, n)
            tb = _eval_expr(entry.metadata.mono_b, fields, n)
            if entry.answer == "EQ":
                assert ta == tb
            else:
                assert ta != tb


def _eval_expr(text, fields, n):
    total = 0
    for term in text.split(" + "):
        term = term.strip()
        if not term:
            continue
        c, _, rest = term.partition("*")
        c = int(c)
        facs = []
        for tok in rest.split("*"):
            fi = FIELD_NAMES.index(tok[0])
            j = tok.index("[")
            k = tok.index("]")
            off = int(tok[j + 1:k])
            facs.append((fi, off))
        total += c * _site_sum(fields, facs, n)
    return total


FIELD_NAMES = ("u", "v")


def test_wrong_and_empty_score_zero():
    obj = _make(3)
    entry = obj.generate_example()
    assert obj.score_answer("", entry) == 0.0
    assert obj.score_answer("garbage", entry) == 0.0
    assert obj.score_answer("maybe", entry) == 0.0
    assert obj.score_answer(entry.answer.lower(), entry) == 1.0


def test_difficulty_changes():
    base = _make(0)
    high = _make(6)
    assert high.config.period > base.config.period
    assert high.config.num_monomials >= base.config.num_monomials
    assert base.generate_example() is not None
    assert high.generate_example() is not None


def test_neq_perturbation_guaranteed_nonzero():
    random.seed(42)
    obj = _make(4)
    for _ in range(20):
        entry = obj.generate_example()
        if entry.answer == "NEQ":
            assert entry.metadata.total_a != entry.metadata.total_b
