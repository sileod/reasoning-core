import numpy as np

from reasoning_core.evaluation import surface_audit as sa


def test_features_one_row_per_option_and_payload_blocks():
    F = sa.features("Facts: a b c.\n\nHypothesis: dog barks", ["dog barks", "cat", "a b"])
    assert F.shape == (3, len(sa.FEATURES))
    col = dict(zip(sa.FEATURES, F.T))
    assert col["overlap_last"][0] == 1 and col["overlap_first"][2] == 1 and col["best_block_is_last"][0] == 1


def _items(n, cue, rng):
    """4 options; with `cue`, half the golds are the longest option."""
    out = []
    for _ in range(n):
        opts = ["x" * int(rng.integers(1, 9)) for _ in range(4)]
        g = int(rng.integers(4))
        if cue and rng.random() < .5:
            opts[g] = "x" * 12
        out.append((sa.features("prompt", opts), g))
    return out


def test_leave_group_out_finds_a_shared_cue_and_gate_removes_it():
    rng = np.random.default_rng(0)
    items = [it for _ in range(4) for it in _items(150, True, rng)]
    groups = np.repeat(list("abcd"), 150)
    assert sa.leave_group_out(items, groups, folds=4).mean() > 0.55
    keep = sa.gate(items, groups, rounds=1)
    assert all(0.2 < keep[groups == g].mean() < 0.7 for g in "abcd")
    survivors = [items[i] for i in np.flatnonzero(keep)]
    assert sa.leave_group_out(survivors, groups[keep], folds=4).mean() < 0.35   # a fresh model is back near chance
    clean = [it for _ in range(4) for it in _items(150, False, rng)]
    assert abs(sa.leave_group_out(clean, groups, folds=4).mean() - 0.25) < 0.08
