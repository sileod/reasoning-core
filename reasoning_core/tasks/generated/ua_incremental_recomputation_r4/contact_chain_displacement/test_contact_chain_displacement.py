import math

import reasoning_core.tasks.generated.ua_incremental_recomputation_r4.contact_chain_displacement.contact_chain_displacement as mod


def _task(level=0):
    t = mod.ContactChainDisplacement()
    if level:
        t.config.set_level(level)
    return t


def test_gold_scores_correct_at_all_levels():
    for level in (0, 2, 5, 6):
        t = _task(level)
        for _ in range(20):
            ex = t.generate_example(level=level)
            assert t.score_answer(ex.answer, ex) == 1.0, (level, ex.answer)


def test_garbage_scores_zero():
    t = _task(0)
    ex = t.generate_example()
    for bad in ("", "garbage", "1,2,3", "import x", "1.0,0.5"):
        assert t.score_answer(bad, ex) == 0.0, bad


def test_fractions_reduced():
    t = _task(0)
    ex = t.generate_example()
    before, after = t.generate_example(), None
    for level in (0, 3, 6):
        t2 = _task(level)
        for _ in range(30):
            e = t2.generate_example(level=level)
            parts = e.answer.split(",")
            fracs = parts[:-1] if e.metadata["blocked"] else parts
            for f in fracs:
                assert "/" not in f or math.gcd(*map(int, f.split("/"))) == 1


def test_blocked_has_stop_label():
    t = _task(3)
    seen_blocked = 0
    for _ in range(300):
        ex = t.generate_example(level=3)
        if ex.metadata["blocked"]:
            seen_blocked += 1
            assert ex.answer.endswith(f"S{ex.metadata['limiter']}")
    assert seen_blocked > 0


def test_displacements_domain():
    t = _task(6)
    for _ in range(50):
        ex = t.generate_example(level=6)
        n = ex.metadata["count"]
        d = ex.metadata["displacements"]
        caps = ex.metadata["caps"]
        assert len(d) == n
        assert all(x >= 0 for x in d)
        for i in range(n):
            if caps[i] >= 0:
                assert d[i] <= caps[i]
        assert ex.metadata["push"] > 0


def test_reproducible_within_seed():
    import random
    random.seed(2072234021)
    a = [_task(0).generate_example().answer for _ in range(5)]
    random.seed(2072234021)
    b = [_task(0).generate_example().answer for _ in range(5)]
    assert a == b
