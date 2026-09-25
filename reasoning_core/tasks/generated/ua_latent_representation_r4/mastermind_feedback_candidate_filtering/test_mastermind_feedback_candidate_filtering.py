def _load():
    from reasoning_core.tasks.generated.ua_latent_representation_r4.mastermind_feedback_candidate_filtering import (
        mastermind_feedback_candidate_filtering as m,
    )
    return m


def test_generate_and_score_all_levels():
    m = _load()
    task = m.MastermindFeedbackCandidateFiltering()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            ans = [c for c in ex.answer.split(",")]
            assert ans == sorted(ans)
            assert len(ans) == ex.metadata["candidate_count"]
            assert task.score_answer(ex.answer, ex) == 1.0


def test_candidates_are_consistent():
    m = _load()
    task = m.MastermindFeedbackCandidateFiltering()
    for _ in range(30):
        ex = task.generate_example()
        fb = ex.metadata["feedback_counts"]
        for code in ex.answer.split(","):
            for i, g in enumerate(ex.metadata["guesses"]):
                e, w = fb[i]
                assert m._feedback(code, g) == (e, w)
        alpha = ex.metadata["alphabet"]
        n = ex.metadata["length"]
        from itertools import product
        all_codes = ["".join(p) for p in product(alpha, repeat=n)]
        for c in all_codes:
            if all(m._feedback(c, g) == (e, w) for (g, (e, w)) in zip(ex.metadata["guesses"], fb)):
                assert c in ex.answer.split(",")


def test_junk_scores_zero():
    m = _load()
    task = m.MastermindFeedbackCandidateFiltering()
    ex = task.generate_example()
    assert task.score_answer("", ex) != 1.0
    assert task.score_answer("garbage", ex) != 1.0


def test_answer_not_readable_off_surface():
    m = _load()
    task = m.MastermindFeedbackCandidateFiltering()
    for _ in range(30):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        last_word = prompt.split()[-1].strip(".,")
        assert last_word != ex.answer


def test_apply_difficulty_changes():
    m = _load()
    cfg = m.MastermindFilterConfig()
    before = (cfg.length, cfg.colors, cfg.base_guesses)
    cfg.set_level(5)
    after = (cfg.length, cfg.colors, cfg.base_guesses)
    assert before != after


def test_alpha_unique_and_valid():
    m = _load()
    task = m.MastermindFeedbackCandidateFiltering()
    for _ in range(30):
        ex = task.generate_example()
        alpha = ex.metadata["alphabet"]
        assert len(alpha) == ex.metadata["colors"]
        assert len(set(alpha)) == len(alpha)
