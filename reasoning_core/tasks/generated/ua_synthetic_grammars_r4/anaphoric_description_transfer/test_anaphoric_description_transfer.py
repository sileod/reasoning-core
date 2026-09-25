import random

from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.anaphoric_description_transfer.anaphoric_description_transfer import (
    AnaphoricDescriptionTransfer,
    AnaphoricDescriptionTransferConfig,
    resolve_chain,
    describe,
)


def test_gold_answers_score_one():
    task = AnaphoricDescriptionTransfer()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_resolution_matches_metadata():
    task = AnaphoricDescriptionTransfer()
    task.config.set_level(5)
    for _ in range(30):
        ex = task.generate_example()
        md = ex.metadata
        assert resolve_chain(md["universe"], md["rels"], md["new_binder"]) == md["answer"]
        assert resolve_chain(md["universe"], md["rels"], md["outer_old"]) == md["answer_old"]
        assert md["answer"] != md["outer_old"]
        assert md["answer"] != md["new_binder"]


def test_chain_describe_len():
    assert describe(["owner"]) == "the owner of"
    assert describe(["owner", "manager"]) == "the manager of the owner of"
    assert describe(["a", "b", "c"]) == "the c of the b of the a of"


def test_junk_scores_zero():
    task = AnaphoricDescriptionTransfer()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("not a name", ex) == 0.0


def test_labels_balanced():
    task = AnaphoricDescriptionTransfer()
    for level in (0, 2, 5):
        task.config.set_level(level)
        answers = {}
        for _ in range(200):
            ex = task.generate_example()
            answers[ex.answer] = answers.get(ex.answer, 0) + 1
        assert len(answers) >= 3, f"level {level}: only {len(answers)} distinct answers"


def test_all_levels_generate():
    task = AnaphoricDescriptionTransfer()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(10):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_difficulty_scales():
    base = AnaphoricDescriptionTransferConfig()
    c0 = AnaphoricDescriptionTransferConfig()
    c0.set_level(0)
    c6 = AnaphoricDescriptionTransferConfig()
    c6.set_level(6)
    assert c6.chain_len >= c0.chain_len
    assert c6.n_entities >= c0.n_entities
