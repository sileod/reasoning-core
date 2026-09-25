import random

from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.semantic_reconstruction_sites.semantic_reconstruction_sites import (
    SemanticReconstructionSites,
)


def test_gold_scores_one():
    task = SemanticReconstructionSites()
    for _ in range(40):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_rejects_wrong_subsets():
    task = SemanticReconstructionSites()
    for _ in range(40):
        ex = task.generate_example()
        gold = set(ex.answer.split())
        all_sites = {s[0] for s in ex.metadata["sites"]}
        assert gold & all_sites == gold
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("reajrjrje9595!", ex) == 0.0
        non = sorted(all_sites - gold)
        if non:
            assert task.score_answer(" ".join(non), ex) == 0.0
        flip = all_sites - gold
        if flip:
            assert task.score_answer(" ".join(sorted(flip)), ex) == 0.0


def test_answer_not_full_and_not_empty():
    task = SemanticReconstructionSites()
    for _ in range(60):
        ex = task.generate_example()
        all_sites = {s[0] for s in ex.metadata["sites"]}
        gold = set(ex.answer.split())
        assert gold
        assert gold != all_sites


def test_survives_json_roundtrip():
    import json
    from easydict import EasyDict as edict
    task = SemanticReconstructionSites()
    ex = task.generate_example()
    rt = edict(json.loads(json.dumps(dict(ex.metadata))))
    nrt = type(ex)(metadata=rt, answer=ex.answer)
    nrt.prompt = ex.prompt
    assert task.score_answer(ex.answer, nrt) == 1.0


def test_deterministic_under_seed():
    task = SemanticReconstructionSites()
    random.seed(1336314872)
    a = task.generate_example()
    random.seed(1336314872)
    b = task.generate_example()
    assert a.answer == b.answer
    assert a.metadata["sites"] == b.metadata["sites"]
    assert a.prompt == b.prompt


def test_all_levels_generate():
    task = SemanticReconstructionSites()
    for level in range(7):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert len(task.tokenizer.encode(ex.prompt)) <= 2048
