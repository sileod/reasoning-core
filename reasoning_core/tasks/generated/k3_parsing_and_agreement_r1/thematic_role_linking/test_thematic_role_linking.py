import random

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.thematic_role_linking.thematic_role_linking import (
    ThematicRoleLinking, design_choice, PREPS, REALIZATIONS)


def _task():
    return ThematicRoleLinking()


def test_gold_scores_one():
    t = _task()
    for _ in range(200):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    t = _task()
    for _ in range(100):
        e = t.generate_example()
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("nonsense answer garbage", e) == 0.0


def test_realizations_covered():
    t = _task()
    seen = set()
    for _ in range(2000):
        e = t.generate_example()
        seen.add(e.metadata["realization"])
    assert seen == set(REALIZATIONS.keys())


def test_answer_marks_obliques():
    t = _task()
    obliques_seen = 0
    for _ in range(300):
        e = t.generate_example()
        if e.metadata["oblique"]:
            obliques_seen += 1
    assert obliques_seen > 0


def test_difficulty_changes_config():
    t = _task()
    base = float(t.config.oblique_chance)
    t.config.set_level(6)
    assert t.config.oblique_chance >= base
    t.config.set_level(0)
    assert t.config.oblique_chance < 0.9


def test_answer_length_matches_roles():
    t = _task()
    for _ in range(300):
        e = t.generate_example()
        n = len(e.metadata["answer_seq"])
        # canonical roles present count equals generated overt args
        assert n >= 2


def test_answer_roles_match_realization():
    t = _task()
    for _ in range(400):
        e = t.generate_example()
        roles_in_answer = set()
        for tok in e.metadata["answer_seq"]:
            base = tok.split(" (")[0]
            roles_in_answer.add(base)
        expected = set(REALIZATIONS[e.metadata["realization"]])
        assert roles_in_answer == expected


def test_oblique_preposition_in_answer():
    t = _task()
    seen_marked = 0
    for _ in range(400):
        e = t.generate_example()
        if e.metadata["oblique"]:
            seen_marked += 1
            for tok in e.metadata["answer_seq"]:
                if " (" in tok:
                    role = tok.split(" (")[0]
                    prep = tok.split(" (")[1][:-1]
                    assert prep in PREPS[role]
    assert seen_marked > 0
