"""Murphy decomposition of forecast Brier score into three components.

A forecaster issues probabilistic forecasts grouped into weighted, already
merged bins. Each bin gives its weight (number of forecasts), mean forecast
and realized positive count. The task separates the total Brier score (mean
squared error) into calibration, resolution and outcome uncertainty, each
reported as a reduced fraction of the total.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


@dataclass
class ForecastDiagnosticConfig(Config):
    num_cohorts: int = 3
    max_weight: int = 2
    forecast_denom: int = 3

    def apply_difficulty(self, level):
        self.num_cohorts = 3 + level
        self.max_weight = 2 + level
        self.forecast_denom = 3 + level


def _build_instance(cfg):
    K = cfg.num_cohorts
    denom = cfg.forecast_denom
    max_n = cfg.max_weight
    for _ in range(1000):
        cohorts = []
        total_n = 0
        total_k = 0
        for _j in range(K):
            n = random.randint(2, max_n)
            r = Fraction(random.randint(0, denom), denom)
            k = random.randint(0, n)
            cohorts.append((n, r.numerator, r.denominator, k))
            total_n += n
            total_k += k
        if total_n <= 0:
            continue
        o_bar = Fraction(total_k, total_n)
        if o_bar == 0 or o_bar == 1:
            continue
        cal = Fraction(0, 1)
        res = Fraction(0, 1)
        for (n, rn, rd, k) in cohorts:
            r = Fraction(rn, rd)
            o = Fraction(k, n)
            cal += n * (r - o) ** 2
            res += n * (o - o_bar) ** 2
        cal = cal / total_n
        res = res / total_n
        unc = o_bar * (1 - o_bar)
        bs = cal + unc - res
        if bs <= 0:
            continue
        f_cal = cal / bs
        f_res = res / bs
        f_unc = unc / bs
        if not (0 <= f_cal <= 1 and 0 <= f_unc <= 1 and f_res >= 0):
            continue
        if f_cal - f_res + f_unc != 1:
            continue
        return cohorts, o_bar, bs, f_cal, f_res, f_unc
    raise RuntimeError("could not construct forecast decomposition instance")


class ForecastDiagnosticDecomposition(Task):
    summary = ("Separate probabilistic forecast error into calibration, "
               "resolution, and outcome uncertainty across weighted cohorts "
               "and merged forecast bins; each component returned as a reduced "
               "fraction of the total mean squared error.")
    design_choice = ("Return the three component values as a canonical string "
                     "in fixed order: calibration, resolution, outcome "
                     "uncertainty, each as a reduced fraction of the total "
                     "mean squared error.")
    config_cls = ForecastDiagnosticConfig

    def generate_entry(self):
        cohorts, o_bar, bs, f_cal, f_res, f_unc = _build_instance(self.config)
        answer = "%d/%d, %d/%d, %d/%d" % (
            f_cal.numerator, f_cal.denominator,
            f_res.numerator, f_res.denominator,
            f_unc.numerator, f_unc.denominator,
        )
        metadata = {
            "num_cohorts": len(cohorts),
            "total_weight": int(sum(c[0] for c in cohorts)),
            "cohorts": [{"weight": n, "r_num": rn, "r_den": rd, "pos": k}
                        for (n, rn, rd, k) in cohorts],
            "o_num": o_bar.numerator,
            "o_den": o_bar.denominator,
            "bs_num": int(bs.numerator),
            "bs_den": int(bs.denominator),
            "cal_n": int(f_cal.numerator),
            "cal_d": int(f_cal.denominator),
            "res_n": int(f_res.numerator),
            "res_d": int(f_res.denominator),
            "unc_n": int(f_unc.numerator),
            "unc_d": int(f_unc.denominator),
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        m = metadata
        lines = [
            "A forecaster issues probabilistic (0-1) forecasts, grouped into "
            "%d bins by rounded forecast value; bins sharing a forecast value "
            "have been merged, so each bin carries a weight equal to the "
            "number of forecasts it contains. For each bin you are given its "
            "weight n, its mean forecast r, and the realized number k of "
            "positive outcomes. The bins (weight, mean forecast, positive "
            "outcomes) are:"
            % m["num_cohorts"],
            "",
        ]
        for i, c in enumerate(m["cohorts"]):
            lines.append(
                "Bin %d: weight %d, forecast %d/%d, positives %d."
                % (i + 1, c["weight"], c["r_num"], c["r_den"], c["pos"])
            )
        lines.append("")
        lines.append(
            "Compute the Murphy decomposition of the Brier score (mean squared "
            "error) into three components. Let N be the total weight, "
            "o = (sum of positives)/N the overall base rate, and for each bin "
            "o_j = k_j/n_j its observed frequency. Then calibration = "
            "(1/N)*sum_j n_j*(r_j - o_j)^2, resolution = "
            "(1/N)*sum_j n_j*(o_j - o)^2, and outcome uncertainty = o*(1-o). "
            "The total Brier score equals calibration + outcome uncertainty "
            "- resolution."
        )
        lines.append("")
        lines.append(
            "Give the three components each as a reduced fraction of the total "
            "Brier score, in the fixed order calibration, resolution, outcome "
            "uncertainty, separated by commas - for example 1/3, 2/5, 4/15."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        a = str(answer).strip()
        if a == entry.answer:
            return 1.0
        gold = [
            (entry.metadata["cal_n"], entry.metadata["cal_d"]),
            (entry.metadata["res_n"], entry.metadata["res_d"]),
            (entry.metadata["unc_n"], entry.metadata["unc_d"]),
        ]
        try:
            parts = [p.strip() for p in a.split(",")]
            if len(parts) != 3:
                return 0.0
            for part, (gn, gd) in zip(parts, gold):
                num_s, den_s = part.split("/")
                if int(num_s) != gn or int(den_s) != gd:
                    return 0.0
            return 1.0
        except Exception:
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'forecast_diagnostic_decomposition (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/forecast_diagnostic_decomposition',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
