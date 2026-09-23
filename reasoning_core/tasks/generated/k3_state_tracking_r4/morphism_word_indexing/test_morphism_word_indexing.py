import importlib

from reasoning_core.template import Entry

mod = importlib.import_module(
    "reasoning_core.tasks.generated.k3_state_tracking_r4."
    "morphism_word_indexing.morphism_word_indexing"
)
MorphismWordIndexing = mod.MorphismWordIndexing


def _run(config=None, level=0):
    task = MorphismWordIndexing(config=config, _level=level)
    task.config.set_level(level)
    return task


def test_scoring_roundtrip():
    task = _run()
    for _ in range(30):
        ex = task.generate_example()
        assert isinstance(ex, Entry)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert isinstance(ex.answer, str) and len(ex.answer) == 1
        assert ex.answer in ex.metadata["alphabet"]


def test_wrong_answers_fail():
    task = _run()
    for _ in range(20):
        ex = task.generate_example()
        wrong = "x"
        if wrong == ex.answer:
            wrong = "y"
        assert task.score_answer(wrong, ex) < 1.0
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("zz", ex) < 1.0


def test_answer_matches_constructed_word():
    for level in (0, 2, 5, 6):
        task = _run(level=level)
        for _ in range(30):
            ex = task.generate_example()
            word = ex.metadata["seed"]
            for _ in range(ex.metadata["n"]):
                word = "".join(ex.metadata["morphism"][c] for c in word)
            k = int(ex.metadata["k_binary"], 2)
            assert word[k] == ex.answer
            assert len(word) == ex.metadata["length"]


def test_validate_all_levels():
    for level in (0, 1, 2, 3, 4, 5, 6):
        task = _run(level=level)
        task.validate(n_samples=4)


def test_difficulty_changes_config():
    base = MorphismWordIndexing(config=MorphismWordIndexing.config_cls())
    base.config.set_level(0)
    c0 = base.config.to_dict()
    base.config.set_level(6)
    c6 = base.config.to_dict()
    assert c0 != c6
    assert c6["max_len"] > c0["max_len"]
