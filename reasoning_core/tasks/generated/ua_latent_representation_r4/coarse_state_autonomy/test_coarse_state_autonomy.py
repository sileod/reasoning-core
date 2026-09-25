import random

from reasoning_core.tasks.generated.ua_latent_representation_r4.coarse_state_autonomy.coarse_state_autonomy import (
    CoarseStateAutonomy,
    _closed,
)


def _gen(level):
    task = CoarseStateAutonomy()
    task.config.set_level(level)
    return task


def test_closed_answer_scores():
    task = _gen(2)
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_recompute_consistency():
    task = _gen(3)
    for _ in range(80):
        e = task.generate_example()
        m = e.metadata
        fine = m["fine_states"]
        coarse = m["coarse_states"]
        agg = m["agg"]
        t = m["fine_t"]
        is_c = _closed(agg, t, fine, coarse)
        if e.answer == "closed":
            assert is_c is True
        else:
            assert is_c is False


def test_wrong_answers_rejected():
    task = _gen(4)
    for _ in range(50):
        e = task.generate_example()
        if e.answer == "closed":
            assert task.score_answer("0,0", e) == 0.0
        else:
            assert task.score_answer("closed", e) == 0.0
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("garbage", e) == 0.0


def test_difficulty_changes_config():
    task = _gen(0)
    low = (task.config.fine_states, task.config.coarse_states)
    task.config.set_level(6)
    high = (task.config.fine_states, task.config.coarse_states)
    assert low != high


def test_all_levels_generate():
    for level in range(7):
        task = _gen(level)
        for _ in range(3):
            e = task.generate_example()
            assert e.answer is not None
            assert task.score_answer(e.answer, e) == 1.0


def test_witness_is_genuinely_ambiguous():
    task = _gen(5)
    for _ in range(60):
        e = task.generate_example()
        if e.answer == "closed":
            continue
        f, c = e.answer.split(",")
        m = e.metadata
        ff, cc = int(f), int(c)
        block = [g for g in range(m["fine_states"]) if m["agg"][g] == m["agg"][ff]]
        outputs = {m["agg"][m["fine_t"][g]] for g in block}
        assert len(outputs) >= 2
        assert m["agg"][m["fine_t"][ff]] == cc


def test_balanced_labels():
    from collections import Counter

    task = _gen(2)
    cnt = Counter()
    for _ in range(120):
        cnt[task.generate_example().answer == "closed"] += 1
    frac = cnt[True] / sum(cnt.values())
    assert 0.0 <= frac <= 0.6
