import json
import random

from reasoning_core.tasks.generated.k3_global_from_local_r4.pedigree_genotype_consistency.pedigree_genotype_consistency import (
    PedigreeConfig,
    PedigreeGenotypeConsistency,
)


def test_config_scales():
    base = PedigreeConfig()
    cfg = PedigreeConfig()
    cfg.set_level(6)
    assert cfg.n_members >= base.n_members
    assert cfg.max_query >= base.max_query
    assert cfg.allow_x == 1


def test_gold_scores_one():
    task = PedigreeGenotypeConsistency()
    for _ in range(40):
        task.config.set_level(random.randint(0, 6))
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_bad_answers_fail():
    task = PedigreeGenotypeConsistency()
    for _ in range(30):
        task.config.set_level(random.randint(0, 6))
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("not a genotype", ex) == 0.0
        tokens = ex.answer.split()
        flipped = tokens[::-1]
        if " ".join(flipped) != ex.answer:
            assert task.score_answer(" ".join(flipped), ex) == 0.0


def test_all_levels_generate():
    task = PedigreeGenotypeConsistency()
    seen = set()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(10):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.answer)
    assert len(seen) > 3


def test_answer_domain():
    task = PedigreeGenotypeConsistency()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            tokens = ex.answer.split()
            assert all(t in ("AA", "Aa", "aa") for t in tokens)
            assert len(tokens) == len(ex.metadata["query"])
            assert len(tokens) == len(ex.metadata["answer_tokens"])


def test_metadata_json_serializable():
    task = PedigreeGenotypeConsistency()
    for level in range(0, 7):
        task.config.set_level(level)
        ex = task.generate_example()
        json.dumps(ex.to_dict())
