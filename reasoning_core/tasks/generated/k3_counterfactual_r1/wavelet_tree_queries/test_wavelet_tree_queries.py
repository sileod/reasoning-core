import reasoning_core.tasks.generated.k3_counterfactual_r1.wavelet_tree_queries.wavelet_tree_queries as wt
from reasoning_core.template import Entry


def _make(level=0, seed=0):
    import random
    random.seed(seed)
    t = wt.WaveletTreeQueries()
    t.config.set_level(level)
    return t, t.generate_entry()


def test_gold_scores_one():
    for level in range(7):
        for seed in range(5):
            t, entry = _make(level, seed)
            assert t.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    t, entry = _make()
    assert t.score_answer("", entry) == 0.0
    assert t.score_answer("banana", entry) == 0.0
    assert t.score_answer("12.5", entry) == 0.0


def test_answer_domain():
    for level in range(7):
        for seed in range(5):
            t, entry = _make(level, seed)
            q = entry.metadata["query"]
            v = int(entry.answer)
            if q == "rank":
                lo, hi = entry.metadata["lo"], entry.metadata["hi"]
                assert 0 <= v <= hi - lo
            elif q == "select":
                symbols = entry.metadata["symbols"]
                lo, hi = 0, len(symbols)
                assert v == -1 or (0 <= v < len(symbols) and symbols[v] == entry.metadata["symbol"])
            else:
                lo, hi = entry.metadata["lo"], entry.metadata["hi"]
                span = entry.metadata["symbols"][lo:hi]
                assert v in span
                assert sum(1 for x in span if x < v) < entry.metadata["k"]
                assert sum(1 for x in span if x <= v) >= entry.metadata["k"]


def test_answer_is_correct():
    for level in range(7):
        for seed in range(8):
            t, entry = _make(level, seed)
            q = entry.metadata["query"]
            symbols = entry.metadata["symbols"]
            v = int(entry.answer)
            if q == "rank":
                expected = sum(1 for s in symbols[entry.metadata["lo"]:entry.metadata["hi"]]
                               if s == entry.metadata["symbol"])
                assert v == expected
            elif q == "select":
                assert v == wt._select(symbols, entry.metadata["symbol"], entry.metadata["occurrence"])
            else:
                assert v == wt._range_quantile(symbols, entry.metadata["lo"], entry.metadata["hi"],
                                               entry.metadata["k"])


def test_difficulty_changes_config():
    t = wt.WaveletTreeQueries()
    t.config.set_level(0)
    base_len, base_alpha = t.config.length, t.config.alphabet_size
    t.config.set_level(6)
    assert t.config.length > base_len
    assert t.config.alphabet_size > base_alpha


def test_metadata_json_serializable():
    import json
    t, entry = _make(5, 3)
    json.dumps(entry.metadata)
