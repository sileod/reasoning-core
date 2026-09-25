import random

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.prediction_commitment_lineage.prediction_commitment_lineage import (
    LineageConfig,
    PredictionCommitmentLineage,
)


def _lineage(parents, v):
    anc = {v}
    stack = list(parents[v])
    while stack:
        x = stack.pop()
        if x not in anc:
            anc.add(x)
            stack.extend(parents[x])
    return anc


def _recompute(entry):
    V = entry.metadata["num_versions"]
    D = entry.metadata["data_pool"]
    parents = entry.metadata["parents"]
    intro = entry.metadata["intro"]
    seen = []
    for v in range(V):
        lin = _lineage(parents, v)
        seen.append({d for d in range(D) if intro[d] in lin})
    pairs = []
    for p in entry.metadata["pairs"]:
        uncont = set(p["access"]).isdisjoint(seen[p["version"]])
        pairs.append(uncont)
    clean = sorted(
        (p["claim"], p["test"])
        for p, uc in zip(entry.metadata["pairs"], pairs)
        if uc
    )
    return ",".join(f"{a}:{b}" for a, b in clean) if clean else "none"


def test_gold_scores_one():
    random.seed(1)
    task = PredictionCommitmentLineage()
    for _ in range(30):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_answer_matches_resolver():
    random.seed(7)
    task = PredictionCommitmentLineage()
    for _ in range(30):
        e = task.generate_example()
        assert e.answer == _recompute(e)


def test_junk_and_empty_score_zero():
    random.seed(2)
    task = PredictionCommitmentLineage()
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("garbage", e) < 1.0


def test_wrong_pair_scores_zero():
    random.seed(3)
    task = PredictionCommitmentLineage()
    for _ in range(20):
        e = task.generate_example()
        gold = e.answer
        if gold == "none":
            assert task.score_answer("1:1", e) < 1.0
            assert task.score_answer("1:1,2:2", e) < 1.0
        else:
            toks = gold.split(",")
            wrong = toks[0] if len(toks) > 1 else "none"
            assert task.score_answer(wrong, e) < 1.0


def test_answer_format_valid():
    random.seed(4)
    task = PredictionCommitmentLineage()
    for _ in range(20):
        e = task.generate_example()
        if e.answer == "none":
            continue
        n_pairs = int(e.metadata["num_claims"])
        for tok in e.answer.split(","):
            c, t = tok.split(":")
            assert 1 <= int(c) <= n_pairs
            assert 1 <= int(t) <= int(e.metadata["num_tests"])


def test_difficulty_changes_config():
    cfg = LineageConfig()
    base = (cfg.num_claims, cfg.num_tests, cfg.num_versions, cfg.data_pool,
            cfg.access_size, cfg.max_parents)
    cfg_hi = LineageConfig()
    cfg_hi.set_level(5)
    hi = (cfg_hi.num_claims, cfg_hi.num_tests, cfg_hi.num_versions, cfg_hi.data_pool,
          cfg_hi.access_size, cfg_hi.max_parents)
    assert base != hi


def test_level0_generates_and_varies():
    random.seed(5)
    task = PredictionCommitmentLineage()
    task.config.set_level(0)
    answers = {task.generate_example().answer for _ in range(20)}
    assert len(answers) >= 2


def test_level6_generates():
    random.seed(6)
    task = PredictionCommitmentLineage()
    task.config.set_level(6)
    e = task.generate_example()
    assert task.score_answer(e.answer, e) == 1.0
