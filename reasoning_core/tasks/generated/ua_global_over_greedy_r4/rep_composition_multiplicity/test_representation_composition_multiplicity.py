import importlib

m = importlib.import_module(
    "reasoning_core.tasks.generated.ua_global_over_greedy_r4."
    "representation_composition_multiplicity.representation_composition_multiplicity"
)

IRREPS = m.IRREPS
CHARS = m.CHARS


def _multiplicity(v, target):
    t = CHARS[target]
    return (v[0] * t[0] + 3 * v[1] * t[1] + 2 * v[2] * t[2]) // m.ORDER


def test_known_decompositions():
    assert _multiplicity(m._power_vec("T", 3, "sym"), "T") == 1
    assert _multiplicity(m._power_vec("E", 2, "ext"), "S") == 1
    assert _multiplicity(m._power_vec("E", 2, "ext"), "T") == 0
    assert _multiplicity(m._power_vec("E", 2, "sym"), "T") == 1
    assert _multiplicity(m._power_vec("E", 2, "sym"), "E") == 1


def test_gold_scores_one():
    t = m.RepCompositionMultiplicityV2()
    for _ in range(30):
        e = t.generate_entry()
        assert t.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    t = m.RepCompositionMultiplicityV2()
    e = t.generate_entry()
    assert t.score_answer("", e) == 0.0
    assert t.score_answer("abc", e) == 0.0
    assert t.score_answer("3.5", e) == 0.0


def test_multiplicity_nonnegative_and_exact():
    t = m.RepCompositionMultiplicityV2()
    for _ in range(200):
        e = t.generate_entry()
        v = [0, 0, 0]
        for rep, op, n in e.metadata["pieces"]:
            pv = m._power_vec(rep, n, op)
            v = [v[i] + pv[i] for i in range(3)]
        m_target = e.metadata["target"]
        dims = {"T": 1, "S": 1, "E": 2}
        total = sum(_multiplicity(v, r) * dims[r] for r in IRREPS)
        assert total == v[0]
        assert _multiplicity(v, m_target) == int(e.answer)
        assert int(e.answer) >= 0
