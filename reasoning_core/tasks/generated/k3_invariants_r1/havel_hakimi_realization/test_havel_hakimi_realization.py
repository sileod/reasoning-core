import random

from reasoning_core.tasks.generated.k3_invariants_r1.havel_hakimi_realization.havel_hakimi_realization import (
    HavelHakimiRealization,
    HavelHakimiConfig,
    hh_trace,
)


def _sanity(entry, task):
    m = entry.metadata
    outcome, info, residuals = hh_trace(m["sequence"])
    if m["outcome"] == "graphical":
        assert outcome == "graphical"
        assert entry.answer == "GRAPHICAL"
        assert int(m["k"]) >= info
    elif m["outcome"] == "fail":
        assert outcome == "fail"
        assert m["residual"] == residuals[m["failing_round"] - 1]
        assert entry.answer == (
            "NOTGRAPHICAL " + ",".join(str(x) for x in m["residual"]) + " index 0"
        )
    else:
        assert outcome == "graphical"
        k = int(m["k"])
        assert 1 <= k < m["completion_rounds"]
        assert m["residual"] == residuals[k]
        assert entry.answer == "RESIDUAL " + ",".join(str(x) for x in m["residual"])


def test_gold_scores_one_all_levels():
    task = HavelHakimiRealization()
    for level in (0, 2, 5):
        cfg = HavelHakimiConfig()
        cfg.set_level(level)
        task.config = cfg
        seen_modes = set()
        for _ in range(40):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0
            _sanity(entry, task)
            seen_modes.add(entry.metadata["outcome"])
        assert seen_modes == {"graphical", "fail", "residual"}


def test_junk_and_wrong_score_zero():
    task = HavelHakimiRealization()
    entry = task.generate_example()
    for bad in ("", " ", "notgraphical 1 index 0", "residual 1", "198498!", str(31337)):
        assert task.score_answer(bad, entry) < 1.0


def test_gold_rejects_its_own_computed_str():
    task = HavelHakimiRealization()
    entry = task.generate_example()
    if entry.metadata["outcome"] == "graphical":
        other = "NOTGRAPHICAL 1 index 0"
    else:
        other = "GRAPHICAL"
    assert task.score_answer(other, entry) < 1.0


def test_difficulty_changes_config():
    cfg = HavelHakimiConfig()
    cfg.set_level(0)
    n0 = cfg.n_vertices
    cfg.set_level(6)
    n6 = cfg.n_vertices
    assert n6 > n0


def test_deterministic_under_seed():
    task = HavelHakimiRealization()
    random.seed(682015719)
    a = [task.generate_example().answer for _ in range(12)]
    random.seed(682015719)
    b = [task.generate_example().answer for _ in range(12)]
    assert a == b


def test_metadata_json_serializable():
    import json

    task = HavelHakimiRealization()
    entry = task.generate_example()
    json.dumps(dict(entry.metadata))


def test_hh_trace_trivial():
    assert hh_trace([1, 1])[0] == "graphical"
    assert hh_trace([0, 0, 0])[0] == "graphical"
    assert hh_trace([2, 2, 2])[0] == "graphical"
    assert hh_trace([1, 1, 1])[0] == "fail"
    assert hh_trace([2, 1, 1, 0])[0] == "graphical"
