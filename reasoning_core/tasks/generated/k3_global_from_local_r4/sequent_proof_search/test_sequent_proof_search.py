from reasoning_core.tasks.generated.k3_global_from_local_r4.sequent_proof_search.sequent_proof_search import (  # noqa: E501
    SequentProofConfig,
    SequentProofSearch,
)


def _fresh(level):
    cfg = SequentProofConfig()
    cfg.set_level(level)
    task = SequentProofSearch()
    task.config = cfg
    return task


def test_round_trip():
    task = _fresh(3)
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_gold_scores_one_all_levels():
    for level in range(7):
        task = _fresh(level)
        for _ in range(25):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
            assert x.metadata.leaf_count >= 1


def test_garbage_scores_zero():
    task = _fresh(3)
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("junk", x) == 0.0
    assert task.score_answer("abc", x) == 0.0
    assert task.score_answer("1.5", x) == 0.0
    assert task.score_answer("-3", x) == 0.0


def test_wrong_answer_zero():
    task = _fresh(3)
    x = task.generate_example()
    wrong = x.metadata.leaf_count + 1
    assert task.score_answer(str(wrong), x) == 0.0


def test_difficulty_changes():
    cfg0 = SequentProofConfig()
    cfg6 = SequentProofConfig()
    cfg0.set_level(0)
    cfg6.set_level(6)
    assert cfg6.tmax > cfg0.tmax
    assert cfg6.enrich_frac >= cfg0.enrich_frac


def test_answer_varies():
    task = _fresh(4)
    answers = set()
    for _ in range(80):
        x = task.generate_example()
        answers.add(x.answer)
    assert len(answers) >= 10


def test_not_constant_per_level():
    for level in range(7):
        task = _fresh(level)
        answers = set()
        for _ in range(50):
            x = task.generate_example()
            answers.add(x.answer)
        assert len(answers) >= 2


def test_answer_is_positive_int():
    task = _fresh(5)
    for _ in range(40):
        x = task.generate_example()
        assert str(int(x.answer)) == x.answer
        assert int(x.answer) >= 1


def test_metadata_json_serializable():
    import json
    task = _fresh(3)
    x = task.generate_example()
    json.dumps(dict(x.metadata))
    json.dumps(x.metadata.payload)


def test_answer_not_readable_off_surface():
    task = _fresh(5)
    for _ in range(30):
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        assert str(x.metadata.leaf_count) not in prompt.split("\nSequent:")[1]
