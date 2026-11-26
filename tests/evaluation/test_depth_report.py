import pytest

from reasoning_core.evaluation import depth_report as dr


def rows(depths, k=4):
    return [{"prompt": "p", "answer": "a", "choices": [f"o{j}" for j in range(k)], "answer_idx": 0, "depth": d}
            for d in depths]


def test_chance_adjusted_accuracy_puts_any_option_count_on_one_scale():
    r = rows([3, 3, 7, 7], k=4)
    report = dr.leg_report(r, {"prediction": [0, 1, 0, 0]})
    assert report["3"]["acc"] == 0.5 and report["3"]["acc_adj"] == pytest.approx((1 - 1 / 3 * 1) / 2)
    assert report["7"]["acc_adj"] == 1.0 and report["all"]["n"] == 4
    two = rows([1, 1], k=2)                       # chance on a binary leg reads 0
    assert dr.leg_report(two, {"prediction": [0, 1]})["all"]["acc_adj"] == 0.0


def test_options_only_twin_gives_context_gain():
    r = rows([1, 1])
    report = dr.leg_report(r, {"prediction": [0, 0]}, optonly={"prediction": [0, 2]})
    assert report["all"]["opt_acc"] == 0.5 and report["all"]["context_gain"] == 0.5


def test_calibration_removes_a_label_prior():
    labels = ["True", "False", "Uncertain"]
    r = [{"prompt": "p", "answer": labels[g], "choices": labels, "answer_idx": g, "depth": 1} for g in (0, 1, 2) * 10]
    # the model always prefers "Uncertain" by 1.0, but its evidence favours the gold by 0.5
    costs = [[(0.0 if j == 2 else 1.0) - (0.5 if j == row["answer_idx"] else 0.0) for j in range(3)] for row in r]
    scores = {"prediction": [min(range(3), key=c.__getitem__) for c in costs], "costs": costs}
    raw = dr.leg_report(r, scores)["all"]
    assert raw["acc"] == pytest.approx(1 / 3)                  # label prior: chance
    cal = dr.leg_report(r, scores, calibrate=True)["all"]
    assert cal["cal_acc"] == 1.0
    twin = {"prediction": [2] * 30, "costs": [[1.0, 1.0, 0.0]] * 30}   # content-free prior from the twin
    assert dr.leg_report(r, scores, optonly=twin, calibrate=True)["all"]["cal_acc"] == 1.0
    assert cal["cal_own_acc"] == 1.0
    flat = {"prediction": [2] * 30, "costs": [[1.0, 1.0, 0.0]] * 30}   # no evidence at all: chance after cal_own
    assert dr.leg_report(r, flat, calibrate=True)["all"]["cal_own_acc"] == pytest.approx(1 / 3)


def test_compare_is_paired_and_groups_by_any_field():
    r = rows([1, 1, 2, 2])
    for row, forced in zip(r, (True, False, True, None)):
        row["audit"] = {"forced_chain": forced}
    out = dr.compare(r, {"prediction": [1, 1, 1, 1]}, {"prediction": [0, 1, 0, 0]})
    assert out["1"]["delta"] == pytest.approx(0.5 * 4 / 3) and out["all"]["n"] == 4
    by = dr.compare(r, {"prediction": [1] * 4}, {"prediction": [0] * 4}, by="audit.forced_chain")
    assert set(by) == {"false", "true", "null", "all"} and by["true"]["n"] == 2


def test_generation_and_nll_legs_report_means_per_group():
    r = [{"prompt": "p", "answer": "1", "depth": d} for d in (2, 2, 30)]
    assert dr.leg_report(r, {"score": [1.0, 0.0, 0.0]})["2"]["score"] == 0.5
    assert dr.leg_report(r, {"nll": [1.0, 3.0, 5.0]})["all"]["nll"] == 3.0


def test_generation_scorer_is_validated_and_hashed_only_when_set(tmp_path):
    from reasoning_core.evaluation.battery import EvalLeg
    path = tmp_path / "g.jsonl"
    path.write_text('{"prompt": "p", "answer": "1"}\n')
    plain = EvalLeg("g", str(path), "generation", "g_em")
    scored = EvalLeg("g", str(path), "generation", "g_em", scorer="first_line")
    assert plain.identifier != scored.identifier
    with pytest.raises(ValueError):
        EvalLeg("g", str(path), "qa_nll", "g_nll", scorer="first_line")
    with pytest.raises(ValueError):
        EvalLeg("g", str(path), "generation", "g_em", scorer="nope")
