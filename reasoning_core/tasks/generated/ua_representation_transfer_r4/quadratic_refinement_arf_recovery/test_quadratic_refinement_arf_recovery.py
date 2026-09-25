import random

from reasoning_core.tasks.generated.ua_representation_transfer_r4.quadratic_refinement_arf_recovery.quadratic_refinement_arf_recovery import (
    QuadraticRefinementArfConfig,
    QuadraticRefinementArfRecovery,
    _arf_from_form,
    _tri_index,
    _qval,
    _make_nondegenerate,
    design_choice,
)


def test_basics():
    task = QuadraticRefinementArfRecovery()
    for _ in range(60):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("x", entry) == 0.0


def test_design_choice_present():
    assert "Gauss sum" in design_choice


def test_nondegenerate_and_arf_consistent():
    for _ in range(80):
        n = random.choice([4, 6])
        coeff, true_arf = _make_nondegenerate(n)
        assert _arf_from_form(coeff, n) == true_arf
        # nondegenerate: Gauss sum must be exactly +/- 2**(n/2)
        g = sum(-1 if _qval(coeff, n, x) else 1 for x in range(1 << n))
        assert abs(abs(g) - (1 << (n // 2))) < 1e-9


def test_both_answers_appear():
    task = QuadraticRefinementArfRecovery()
    answers = set()
    for _ in range(80):
        answers.add(task.generate_example().answer)
    assert answers == {"0", "1"}


def test_metadata_json_serializable():
    import json

    task = QuadraticRefinementArfRecovery()
    for _ in range(30):
        entry = task.generate_example()
        json.dumps(entry.metadata)
        assert isinstance(entry.answer, str)
        assert entry.answer in ("0", "1")


def test_difficulty_changes_config():
    cfg = QuadraticRefinementArfConfig()
    cfg.set_level(0)
    base = cfg.n
    cfg.set_level(6)
    assert cfg.n >= base


def test_levels_generate_and_even_dim():
    task = QuadraticRefinementArfRecovery()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert entry.metadata["n"] % 2 == 0


def test_tri_index_roundtrip():
    n = 6
    m = n * (n - 1) // 2
    filled = [0] * m
    for i in range(n):
        for j in range(i + 1, n):
            filled[_tri_index(i, j, n)] = 1
    assert sum(filled) == m


def test_spinsign_consistent_with_form():
    task = QuadraticRefinementArfRecovery()
    for _ in range(60):
        task.config.set_level(0)
        entry = task.generate_example()
        n = entry.metadata["n"]
        gold = entry.metadata["arf"]
        d = entry.metadata["data"]
        if d["type"] == "spinsign":
            g = sum(1 if s == "+" else -1 for s in d["sign"])
            assert (g > 0) == (gold == 0)
            assert abs(abs(g) - (1 << (n // 2))) < 1e-9


def test_spinsign_prompt_answers():
    import json
    task = QuadraticRefinementArfRecovery()
    # force a spinsign instance via direct generation loop
    found = False
    for _ in range(200):
        task.config.set_level(6)
        entry = task.generate_example()
        if entry.metadata["type"] == "spinsign":
            found = True
            d = entry.metadata["data"]
            assert len(d["sign"]) == (1 << d["n"])
            g = sum(1 if s == "+" else -1 for s in d["sign"])
            assert (g > 0) == (entry.metadata["arf"] == 0)
            prompt = task.render_prompt(entry.metadata)
            assert prompt.count("Arf invariant as a single bit") == 1
            assert task.score_answer(entry.answer, entry) == 1.0
            json.dumps(entry.metadata)
            break
    assert found
