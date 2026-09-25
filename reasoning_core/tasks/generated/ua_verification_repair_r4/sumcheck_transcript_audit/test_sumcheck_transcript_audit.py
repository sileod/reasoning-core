import random

from reasoning_core.tasks.generated.ua_verification_repair_r4.sumcheck_transcript_audit.sumcheck_transcript_audit import (
    SumcheckTranscriptAudit,
)


def _make(task, level, seed):
    cfg = task.config_cls()
    cfg.set_level(level)
    task.config = cfg
    random.seed(seed)
    return task.generate_example()


def _score(task, entry):
    return task.score_answer(entry.answer, entry)


def test_consistent_gold_scores_one():
    task = SumcheckTranscriptAudit()
    found = 0
    tries = 0
    while found == 0 and tries < 200:
        x = _make(task, 2, tries + 1)
        if x.metadata["mode"] == 0:
            found = 1
            assert x.answer == "consistent"
            assert _score(task, x) == 1.0
        tries += 1
    assert found == 1


def test_inconsistent_gold_scores_one():
    task = SumcheckTranscriptAudit()
    found = 0
    for seed in range(1, 300):
        x = _make(task, 2, seed)
        if x.metadata["mode"] == 1:
            assert _score(task, x) == 1.0
            found += 1
            if found >= 3:
                break
    assert found >= 3


def test_missing_coeff_gold_scores_one():
    task = SumcheckTranscriptAudit()
    found = 0
    for seed in range(1, 300):
        x = _make(task, 2, seed)
        if x.metadata["mode"] == 2:
            assert _score(task, x) == 1.0
            assert _valid_coeff_domain(x)
            found += 1
            if found >= 3:
                break
    assert found >= 3


def _valid_coeff_domain(x):
    p = x.metadata["p"]
    if x.metadata["mode"] == 2:
        v = x.metadata["rounds"][-1]["hidden_val"]
        return 0 <= (v % p) < p
    return True


def test_all_modes_reachable_level6():
    task = SumcheckTranscriptAudit()
    seen = set()
    for seed in range(1, 200):
        x = _make(task, 6, seed)
        seen.add(x.metadata["mode"])
        if len(seen) == 3:
            break
    assert seen == {0, 1, 2}


def test_junk_scores_zero():
    task = SumcheckTranscriptAudit()
    for seed in range(1, 40):
        x = _make(task, 2, seed)
        assert task.score_answer("", x) == 0.0
        assert task.score_answer("??", x) == 0.0


def test_reproducible_same_seed():
    task = SumcheckTranscriptAudit()
    a = _make(task, 3, 7)
    b = _make(task, 3, 7)
    assert a.answer == b.answer
    drop = {"_time"}
    am = {k: v for k, v in a.metadata.items() if k not in drop}
    bm = {k: v for k, v in b.metadata.items() if k not in drop}
    assert am == bm


def test_missing_coeff_value_is_forced():
    from reasoning_core.tasks.generated.ua_verification_repair_r4.sumcheck_transcript_audit.sumcheck_transcript_audit import _eval_poly

    task = SumcheckTranscriptAudit()
    cfg = task.config_cls()
    cfg.set_level(3)
    task.config = cfg
    found = 0
    for seed in range(1, 200):
        random.seed(seed)
        x = task.generate_example()
        if x.metadata["mode"] != 2:
            continue
        p = x.metadata["p"]
        rounds = x.metadata["rounds"]
        last = rounds[-1]
        coeffs = list(last["coeffs"])
        pos = last["missing_idx"]
        hidden = last["hidden_val"]
        claim = last["claim"] % p
        # other coefficients known; solve for the missing one so f(0)+f(1)==claim
        known_sum = (_eval_poly(coeffs, 0, p) - coeffs[pos] + _eval_poly(coeffs, 1, p) - coeffs[pos]) % p
        # f(0)+f(1) = known_sum + (1+1)*missing  (missing appears once in f(0), once in f(1))
        solved = (claim - known_sum) * pow(2, p - 2, p) % p
        assert solved == hidden % p
        found += 1
        if found >= 5:
            break
    assert found >= 5


def test_inconsistent_round_is_real_first_bad():
    from reasoning_core.tasks.generated.ua_verification_repair_r4.sumcheck_transcript_audit.sumcheck_transcript_audit import _eval_poly, _sum_01_deg1_check

    task = SumcheckTranscriptAudit()
    cfg = task.config_cls()
    cfg.set_level(4)
    task.config = cfg
    for seed in range(1, 120):
        random.seed(seed)
        x = task.generate_example()
        if x.metadata["mode"] != 1:
            continue
        p = x.metadata["p"]
        consistent, first_bad = _sum_01_deg1_check(x.metadata["rounds"], x.metadata["sum"], p)
        assert not consistent
        assert int(x.answer) == first_bad
