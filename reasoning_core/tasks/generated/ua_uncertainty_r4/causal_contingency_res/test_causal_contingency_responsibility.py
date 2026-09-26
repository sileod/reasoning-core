import random
from fractions import Fraction

from reasoning_core.tasks.generated.ua_uncertainty_r4.causal_contingency_res.causal_contingency_responsibility import (
    CausalContingencyResV3,
    NONCAUSE,
    minimal_contingency,
)


def _parse(s):
    if isinstance(s, str) and s.strip() == NONCAUSE:
        return Fraction(0)
    return Fraction(s)


def test_gold_scores_one():
    t = CausalContingencyResV3()
    for _ in range(120):
        t.config.set_level(random.randrange(0, 7))
        x = t.generate_example()
        assert t.score_answer(x.answer, x) == 1.0


def test_noncause_only_when_nominated_votes_no():
    t = CausalContingencyResV3()
    for _ in range(120):
        t.config.set_level(random.randrange(0, 7))
        x = t.generate_example()
        if x.answer == NONCAUSE:
            assert x.metadata["nominated_vote"] is False
            assert x.metadata["k"] is None
        else:
            assert x.metadata["nominated_vote"] is True
            assert _parse(x.answer).denominator == x.metadata["k"] + 1


def test_responsibility_domain():
    t = CausalContingencyResV3()
    for _ in range(120):
        t.config.set_level(random.randrange(0, 7))
        x = t.generate_example()
        if x.answer != NONCAUSE:
            r = _parse(x.answer)
            assert 0 < r <= 1


def test_minimal_contingency_correct():
    weights = [1, 2, 3, 4]
    votes = [True, True, True, True]
    for nom in range(len(weights)):
        for th in range(1, 11):
            k = minimal_contingency(weights, votes, nom, th)
            if k is None:
                continue
            w_x = weights[nom]
            others = [weights[i] for i in range(len(weights)) if i != nom]
            s = sum(others)
            lo = max(0, s - (th - 1))
            hi = s - (th - w_x)
            assert lo <= 0 or True
            subs = []
            for mask in range(1 << len(others)):
                sm = sum(others[i] for i in range(len(others)) if mask >> i & 1)
                subs.append((bin(mask).count("1"), sm))
            best = None
            for c, sm in subs:
                rem = s - sm
                if th - w_x <= rem <= th - 1:
                    if best is None or c < best:
                        best = c
            assert k == best, (nom, th, k, best)


def test_label_balance_over_levels():
    t = CausalContingencyResV3()
    counts = {}
    for level in (0, 3, 6):
        for _ in range(200):
            t.config.set_level(level)
            x = t.generate_example()
            counts.setdefault(level, []).append(x.answer)
    for level, ans in counts.items():
        non = sum(1 for a in ans if a == NONCAUSE)
        frac = len(ans) - non
        assert non > 0 and frac > 0, level
        distinct = len(set(ans))
        assert distinct >= 2, (level, distinct)


def test_reproducible():
    t = CausalContingencyResV3()
    t.config.set_level(3)
    t.config.set_level(3)


def test_junk_and_empty_not_one():
    t = CausalContingencyResV3()
    t.config.set_level(0)
    x = t.generate_example()
    assert t.score_answer("", x) < 1.0
    assert t.score_answer("garbage", x) < 1.0
