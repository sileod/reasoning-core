import collections
import json

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.stepwise_rejection_set.stepwise_rejection_set import (
    StepwiseRejectionSet,
    _reject,
    _bonferroni,
    _holm,
    _bh,
    _parse,
)


def _make(seed=0, n=12, level=None):
    import random

    task = StepwiseRejectionSet()
    if level is not None:
        task.config.set_level(level)
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        rng.random()
        out.append(task.generate_example())
    return out


def _score(ex):
    return StepwiseRejectionSet().score_answer(ex.answer, ex)


def test_generate_and_score_roundtrip():
    for ex in _make(n=20):
        assert _score(ex) == 1.0
        assert ex.metadata["rule"] in ("bonferroni", "holm", "bh")


def test_rules_are_independently_verified():
    for level in range(7):
        for ex in _make(seed=level, n=10, level=level):
            got = _reject(ex.metadata["pvalues"], ex.metadata["rule"], ex.metadata["alpha"])
            assert got == _parse(ex.answer)
            assert got == sorted(got)
            assert 1 <= (min(got) if got else 2)
            assert (max(got) if got else 1) <= ex.metadata["n"]


def test_all_levels_produce_every_rule_and_varied_sizes():
    for level in range(7):
        rules = set()
        sizes = set()
        for ex in _make(seed=100 + level, n=30, level=level):
            rules.add(ex.metadata["rule"])
            sizes.add(len(_parse(ex.answer)))
        assert rules == {"bonferroni", "holm", "bh"}, level
        assert len(sizes) >= 2, (level, sizes)


def test_rule_semantics_matched():
    import random

    random.seed(7)
    for _ in range(60):
        n = random.randint(4, 16)
        p = [random.random() for _ in range(n)]
        a = random.choice((0.01, 0.05, 0.10))
        bf = _bonferroni(p, a)
        ho = _holm(p, a)
        bh = _bh(p, a)
        assert bf == sorted(bf)
        assert ho == sorted(ho)
        assert bh == sorted(bh)
        assert _reject(p, "bonferroni", a) == bf
        assert _reject(p, "holm", a) == ho
        assert _reject(p, "bh", a) == bh


def test_metadata_json_serializable():
    for ex in _make(n=10):
        json.dumps(ex.metadata)


def test_scoring_variants_and_junk():
    task = StepwiseRejectionSet()
    exs = _make(n=20)
    gold = _parse(exs[0].answer)
    assert task.score_answer(str([x for x in gold][::-1] if gold else []), exs[0]) == 1.0
    assert task.score_answer("garbage", exs[0]) == 0.0
    assert task.score_answer("", exs[0]) == 0.0
    assert task.score_answer(None, exs[0]) == 0.0
    assert task.score_answer("[999]", exs[0]) == 0.0


def test_pvalues_are_distinct_and_in_domain():
    for ex in _make(n=30):
        pvs = ex.metadata["pvalues"]
        assert len(set(pvs)) == len(pvs), "tie-free p-values remove Holm/BH tie ambiguity"
        assert all(0.0 < p <= 1.0 for p in pvs), pvs


def test_level_changes_config():
    task = StepwiseRejectionSet()
    t0 = task.config.n
    task.config.set_level(6)
    assert task.config.n >= t0
    assert task.config.n == 16


def test_rejection_set_is_not_readable_off_the_surface():
    counts = collections.Counter()
    for ex in _make(n=40):
        ans = tuple(_parse(ex.answer))
        counts[ans] += 1
    top = counts.most_common(1)[0][1]
    assert top < 20, "a single rejection set should not dominate the distribution"
    for ex in _make(n=40):
        ans = tuple(_parse(ex.answer))
        counts[ans] += 1
    top = counts.most_common(1)[0][1]
    assert top < 20, "a single rejection set should not dominate the distribution"
    # answering with the largest p-value's index must not be systematically correct
    largest_hit = 0
    for ex in _make(n=40):
        pvs = ex.metadata["pvalues"]
        max_idx = pvs.index(max(pvs)) + 1
        if _parse(ex.answer) == [max_idx]:
            largest_hit += 1
    assert largest_hit < 8, largest_hit
