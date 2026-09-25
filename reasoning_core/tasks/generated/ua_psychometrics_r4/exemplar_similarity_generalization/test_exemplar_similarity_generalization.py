import random
import json

from reasoning_core.tasks.generated.ua_psychometrics_r4.exemplar_similarity_generalization.exemplar_similarity_generalization import (
    ExemplarSimilarityGeneralization,
    _category_scores,
    _contribution,
)


def test_generate_and_roundtrip():
    random.seed(1662004003)
    task = ExemplarSimilarityGeneralization()
    x = task.generate_example(level=0)
    assert x.answer in ("A", "B")
    assert task.score_answer(x.answer, x) == 1.0
    rt = json.loads(json.dumps(dict(x.metadata)))
    assert task.score_answer(x.answer, {"answer": x.answer, "metadata": rt}) is not None


def test_score_rejects_junk():
    random.seed(7)
    task = ExemplarSimilarityGeneralization()
    x = task.generate_example(level=3)
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("garbage", x) < 1.0
    assert task.score_answer(None, x) < 1.0
    wrong = "B" if x.answer == "A" else "A"
    assert task.score_answer(wrong, x) < 1.0


def test_difficulty_changes_config():
    task = ExemplarSimilarityGeneralization()
    c0 = task.config.to_dict()
    task.config.set_level(0)
    task.config.set_level(6)
    assert task.config.to_dict() != c0


def test_all_levels_generate():
    random.seed(42)
    task = ExemplarSimilarityGeneralization()
    for level in (0, 1, 2, 3, 4, 5, 6):
        x = task.generate_example(level=level)
        assert task.score_answer(x.answer, x) == 1.0


def test_both_labels_appear():
    random.seed(11)
    task = ExemplarSimilarityGeneralization()
    task.config.set_level(5)
    labels = {task.generate_example().answer for _ in range(60)}
    assert "A" in labels and "B" in labels


def test_answer_reproduces_computation():
    random.seed(5)
    task = ExemplarSimilarityGeneralization()
    task.config.set_level(4)
    for _ in range(30):
        x = task.generate_example()
        md = x.metadata
        missing = {d for d, v in enumerate(md["stimulus"]) if v is None}
        novel = [0 if v is None else v for v in md["stimulus"]]
        sums = _category_scores(md["weights"], [(e["label"], e["values"]) for e in md["exemplars"]],
                                novel, missing, md["kernel"], md["val_max"])
        expected = "A" if sums["A"] > sums["B"] else "B"
        assert x.answer == expected
