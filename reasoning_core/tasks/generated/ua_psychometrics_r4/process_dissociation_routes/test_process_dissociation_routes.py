from fractions import Fraction

from reasoning_core.tasks.generated.ua_psychometrics_r4.process_dissociation_routes.process_dissociation_routes import (
    ProcessDissociationRoutes,
)


def _expected(md):
    a = Fraction(md["a"], 100)
    c = Fraction(md["c"], 100)
    n = md["n"]
    if md["route_type"] == "serial":
        return (1 - c) * (1 - (1 - a) ** n)
    any_ = 1 - (1 - a) ** n * (1 - c)
    return (1 - (1 - a) ** n) / any_


def test_gold_scores_1_all_levels():
    for level in range(7):
        t = ProcessDissociationRoutes()
        t.config.set_level(level)
        for _ in range(200):
            e = t.generate_example()
            assert t.score_answer(e.answer, e) == 1.0


def test_answer_math_correct():
    t = ProcessDissociationRoutes()
    t.config.set_level(4)
    for _ in range(500):
        e = t.generate_example()
        md = e.metadata
        want = _expected(md)
        assert 0 < want < 1, md
        got = Fraction(md["p_auto"][0], md["p_auto"][1])
        assert got == want, (md, got, want)


def test_answer_is_reduced_fraction():
    t = ProcessDissociationRoutes()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(200):
            e = t.generate_example()
            num, den = e.answer.split("/")
            assert num.isdigit() and den.isdigit()
            assert Fraction(int(num), int(den)).denominator == int(den), e.answer


def test_junk_and_empty_score_0():
    t = ProcessDissociationRoutes()
    for level in range(7):
        t.config.set_level(level)
        e = t.generate_example()
        assert t.score_answer("", e) < 1.0
        assert t.score_answer("garbage", e) < 1.0
        assert t.score_answer("1", e) < 1.0
        assert t.score_answer("7/0", e) < 1.0


def test_both_route_types_at_every_level():
    t = ProcessDissociationRoutes()
    for level in range(7):
        t.config.set_level(level)
        routes = set()
        for _ in range(300):
            routes.add(t.generate_example().metadata["route_type"])
        assert routes == {"serial", "parallel"}


def test_difficulty_changes_config():
    t = ProcessDissociationRoutes()
    t.config.set_level(0)
    l0 = (t.config.max_inclusion, t.config.max_attempts)
    t.config.set_level(6)
    l6 = (t.config.max_inclusion, t.config.max_attempts)
    assert l0 != l6
    assert l6[0] > l0[0] and l6[1] > l0[1]


def test_levels_generate_and_denominator_bounded():
    t = ProcessDissociationRoutes()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(100):
            e = t.generate_example()
            num, den = e.answer.split("/")
            assert int(den) <= 4000
            assert int(num) >= 1 and int(num) < int(den)


def test_distractors_exclude_gold_and_stay_in_domain():
    t = ProcessDissociationRoutes()
    t.config.set_level(3)
    for _ in range(200):
        e = t.generate_example()
        gold = Fraction(e.metadata["p_auto"][0], e.metadata["p_auto"][1])
        seen = set()
        for d in t.distractor_candidates(e):
            f = Fraction(int(d.split("/")[0]), int(d.split("/")[1]))
            assert f != gold
            assert 0 < f < 1
            seen.add(f)
        assert len(seen) >= 2
