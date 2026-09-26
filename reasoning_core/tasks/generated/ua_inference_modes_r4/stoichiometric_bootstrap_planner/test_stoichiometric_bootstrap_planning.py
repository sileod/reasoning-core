from reasoning_core.tasks.generated.ua_inference_modes_r4.stoichiometric_bootstrap_planner.stoichiometric_bootstrap_planning import (
    StoichiometricBootstrapPlannerV2,
    _check_solution,
    _canon_answer,
)


def _parse_answer(answer):
    out = []
    for tok in answer.split(","):
        if not tok:
            return None
        idx = tok.find("x")
        if idx <= 0:
            return None
        name = tok[:idx]
        cnt = tok[idx + 1:]
        if not name or not cnt.isdigit():
            return None
        out.append((name, int(cnt)))
    return out


def test_generation_all_levels():
    for level in range(0, 7):
        t = StoichiometricBootstrapPlannerV2()
        t.config.set_level(level)
        ex = t.generate_example()
        assert ex.answer, "answer must be non-empty"
        assert t.score_answer(ex.answer, ex) == 1.0


def test_score_wrong_answers():
    t = StoichiometricBootstrapPlannerV2()
    for _ in range(20):
        ex = t.generate_example()
        assert t.score_answer("", ex) == 0.0
        assert t.score_answer("garbage", ex) == 0.0
        assert t.score_answer("R1x2,R2x3,R4x1", ex) == 0.0
        assert t.score_answer("1,2,3", ex) == 0.0


def test_canon_order_is_sorted():
    c = _canon_answer(["R3", "R1", "R2"], [2, 1, 4])
    assert c == "R1x1,R2x4,R3x2"


def test_parse():
    assert _parse_answer("R1x2,R3x1,R2x4") == [("R1", 2), ("R3", 1), ("R2", 4)]
    assert _parse_answer("bad") is None


def test_solution_verification():
    t = StoichiometricBootstrapPlannerV2()
    for _ in range(10):
        ex = t.generate_example()
        sol = dict(_parse_answer(ex.answer))
        species = ex.metadata["species"]
        name_to_idx = {name: i for i, name in enumerate(species)}
        kinds = {name_to_idx[s]: k for s, k in ex.metadata["kind"].items()}
        reactions = []
        for r in ex.metadata["reactions"]:
            reactions.append({
                "cons": {name_to_idx[s]: k for s, k in r["cons"].items()},
                "prod": {name_to_idx[s]: k for s, k in r["prod"].items()},
            })
        sol_idx = {}
        for name, cnt in sol.items():
            for i, r in enumerate(ex.metadata["reactions"]):
                if r["name"] == name:
                    sol_idx[i] = cnt
        loan = {name_to_idx[s]: k for s, k in ex.metadata["loan"].items()}
        sol_list = [sol_idx.get(i, 0) for i in range(len(reactions))]
        ok = _check_solution(
            reactions, kinds, name_to_idx["T"],
            ex.metadata["target_qty"], ex.metadata["waste_cap"], loan,
            sol_list, t.config.fire_budget,
        )
        assert ok, "gold answer must satisfy all constraints"


def test_summary_and_design_choice():
    assert isinstance(StoichiometricBootstrapPlannerV2.summary, str)
    assert isinstance(StoichiometricBootstrapPlannerV2.design_choice, str)
