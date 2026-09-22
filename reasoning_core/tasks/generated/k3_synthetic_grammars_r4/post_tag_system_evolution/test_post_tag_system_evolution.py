import random

from reasoning_core.tasks.generated.k3_synthetic_grammars_r4.post_tag_system_evolution.post_tag_system_evolution import (
    PostTagSystemEvolution,
    simulate,
)

TASK = PostTagSystemEvolution


def test_gold_scoring_level0():
    random.seed(1)
    t = TASK()
    for _ in range(50):
        ex = t.generate_example()
        assert t.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    random.seed(2)
    t = TASK()
    for _ in range(30):
        ex = t.generate_example()
        assert t.score_answer("zzz", ex) < 1.0
        assert t.score_answer("", ex) < 1.0


def test_difficulty_changes_config():
    base = TASK().config
    t = TASK()
    t.config.set_level(0)
    l0 = (t.config.word_len, t.config.max_steps)
    t.config.set_level(6)
    l6 = (t.config.word_len, t.config.max_steps)
    assert l0 != l6


def test_verifier_holds():
    random.seed(3)
    t = TASK()
    for _ in range(30):
        ex = t.generate_example()
        meta = ex.metadata
        word = meta["word0"]
        m = meta["m"]
        prods = {s: meta["productions"][s] for s in meta["productions"]}
        if meta["mode"] == "word_after":
            k = meta["k"]
            got = simulate(word, m, prods, k)[0]
            assert (got if got else "empty") == ex.answer
        elif meta["mode"] == "steps_halt":
            _, steps, halted = simulate(word, m, prods, meta["m"] * 100)
            assert halted and steps == int(ex.answer)
        else:
            final = simulate(word, m, prods, meta["m"] * 100)[0]
            assert (final if final else "empty") == ex.answer


def test_modes_and_answer_variety():
    random.seed(4)
    t = TASK()
    modes = set()
    answers = set()
    for _ in range(120):
        ex = t.generate_example()
        modes.add(ex.metadata["mode"])
        answers.add(ex.answer)
    assert modes == {"word_after", "steps_halt", "outcome"}
    assert len(answers) > 5
