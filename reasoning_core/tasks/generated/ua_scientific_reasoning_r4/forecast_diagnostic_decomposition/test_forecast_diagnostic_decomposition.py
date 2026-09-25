import random
from fractions import Fraction

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.forecast_diagnostic_decomposition.forecast_diagnostic_decomposition import (
    ForecastDiagnosticConfig,
    ForecastDiagnosticDecomposition,
)


def test_generate_and_score():
    task = ForecastDiagnosticDecomposition()
    for level in range(7):
        cfg = ForecastDiagnosticConfig()
        cfg.set_level(level)
        task.config = cfg
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_components_sum_to_mse():
    task = ForecastDiagnosticDecomposition()
    cfg = ForecastDiagnosticConfig()
    cfg.set_level(5)
    task.config = cfg
    e = task.generate_example()
    f_cal = Fraction(e.metadata["cal_n"], e.metadata["cal_d"])
    f_res = Fraction(e.metadata["res_n"], e.metadata["res_d"])
    f_unc = Fraction(e.metadata["unc_n"], e.metadata["unc_d"])
    assert f_cal - f_res + f_unc == 1


def test_garbage_not_scored():
    task = ForecastDiagnosticDecomposition()
    cfg = ForecastDiagnosticConfig()
    cfg.set_level(3)
    task.config = cfg
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("banana", e) < 1.0
    assert task.score_answer(None, e) < 1.0


def test_difficulty_changes():
    cfg = ForecastDiagnosticConfig()
    base = ForecastDiagnosticConfig()
    cfg.set_level(6)
    assert cfg.num_cohorts > base.num_cohorts
    assert cfg.max_weight >= base.max_weight
    assert cfg.forecast_denom >= base.forecast_denom


def test_metadata_json_serializable():
    import json

    task = ForecastDiagnosticDecomposition()
    cfg = ForecastDiagnosticConfig()
    cfg.set_level(4)
    task.config = cfg
    e = task.generate_example()
    json.dumps(e.metadata)


def test_deterministic_under_seed():
    random.seed(1234)
    task = ForecastDiagnosticDecomposition()
    cfg = ForecastDiagnosticConfig()
    cfg.set_level(5)
    task.config = cfg
    a1 = task.generate_example().answer
    random.seed(1234)
    a2 = task.generate_example().answer
    assert a1 == a2
