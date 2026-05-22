import argparse
import json
import math
from collections import Counter

import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path")
    parser.add_argument("--baseline", choices=("power", "poly"), default="power")
    parser.add_argument("--power_skip", type=int, default=10)
    parser.add_argument("--min_count", type=int, default=2)
    parser.add_argument("--top_k", type=int, default=20)
    args = parser.parse_args()

    result = analyze_log_path(
        args.log_path,
        baseline=args.baseline,
        power_skip=args.power_skip,
        min_count=args.min_count,
    )
    print(format_recommendations(result, top_k=args.top_k))


def analyze_log_path(log_path, baseline="power", power_skip=10, min_count=2, step_df=2):
    rows = load_rows(log_path)
    if not rows:
        raise ValueError(f"No rows found in {log_path}")
    return fit_effects(rows, baseline=baseline, power_skip=power_skip, min_count=min_count, step_df=step_df)


def load_rows(log_path):
    rows = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def fit_effects(rows, baseline="power", power_skip=10, min_count=2, step_df=2):
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["eval_main_loss_delta", "eval_main_loss"]).copy()
    if df.empty:
        raise ValueError("No rows with eval_main_loss_delta and eval_main_loss")

    df["expected_delta"] = _expected_delta(df, baseline=baseline, power_skip=power_skip, step_df=step_df)
    df["excess_delta"] = df["eval_main_loss_delta"].astype(float) - df["expected_delta"].astype(float)

    design, counts, terms = _build_design(df, min_count=min_count)
    y = df["excess_delta"].to_numpy(dtype=float)
    beta, stderr = _ols(y, design.to_numpy(dtype=float))
    coef = pd.Series(beta, index=design.columns)
    se = pd.Series(stderr, index=design.columns)

    out = []
    for col, meta in terms.items():
        effect = float(coef[col])
        standard_error = float(se[col])
        z = effect / standard_error if standard_error > 0 else 0.0
        out.append({
            "task": meta["task"],
            "ratio": meta["ratio"],
            "effect": effect,
            "stderr": standard_error,
            "z": z,
            "p": math.erfc(abs(z) / math.sqrt(2.0)),
            "n": int(counts[col]),
        })

    result = pd.DataFrame(out)
    if result.empty:
        raise ValueError("No task ratio terms with enough observations")
    result["abs_z"] = result["z"].abs()
    result = result.sort_values(["abs_z", "n", "task"], ascending=[False, False, True])
    return result


def format_recommendations(result, top_k=20):
    cols = ["task", "ratio", "effect", "stderr", "z", "p", "n"]
    view = result.head(top_k).copy()
    return view[cols].to_string(index=False, float_format=lambda x: f"{x:.4g}")


def _expected_delta(df, baseline, power_skip, step_df):
    if baseline == "power":
        fitted = _fit_power_curve(df, skip=power_skip)
        if fitted is not None:
            return pd.Series(fitted, index=df.index).diff().fillna(0.0)
    return _poly_expected_delta(df, step_df=step_df)


def _fit_power_curve(df, skip):
    if len(df) <= skip + 4:
        return None
    try:
        from scipy.optimize import curve_fit
    except Exception:
        return None

    step = df["step"].to_numpy(dtype=float)
    loss = df["eval_main_loss"].to_numpy(dtype=float)
    x = np.maximum(step - step.min() + 1.0, 1.0)
    fit_x = x[skip:]
    fit_y = loss[skip:]

    def curve(t, c, a, b):
        return c + a * np.power(t, -b)

    try:
        params, _ = curve_fit(
            curve,
            fit_x,
            fit_y,
            p0=(float(fit_y[-1]), float(max(fit_y[0] - fit_y[-1], 1e-3)), 0.5),
            bounds=([-np.inf, 0.0, 0.01], [np.inf, np.inf, 3.0]),
            maxfev=20000,
        )
    except Exception:
        return None
    return curve(x, *params)


def _poly_expected_delta(df, step_df):
    step = df["step"].astype(float)
    loss = df["eval_main_loss"].astype(float)
    if step.nunique() <= 1:
        return pd.Series(0.0, index=df.index)
    x = ((step - step.min()) / (step.max() - step.min())).to_numpy(dtype=float)
    degree = max(1, min(int(step_df), max(1, len(df) - 2)))
    coef = np.polyfit(x, loss.to_numpy(dtype=float), deg=degree)
    fitted = np.polyval(coef, x)
    return pd.Series(fitted, index=df.index).diff().fillna(0.0)


def _build_design(df, min_count):
    assignments = [_assignments(row) for _, row in df.iterrows()]
    lag1 = [_assignments(row, lag=1) for _, row in df.iterrows()]
    lag2 = [_assignments(row, lag=2) for _, row in df.iterrows()]
    empirical_ratios = _empirical_ratios(df)

    current_terms = _collect_terms(assignments)
    counts = {term: sum(term in row for row in assignments) for term in current_terms}
    current_terms = [term for term in current_terms if counts[term] >= min_count]

    parts = [pd.Series(1.0, index=df.index, name="intercept")]
    terms = {}
    for term in current_terms:
        col = _col_name("cur", term)
        parts.append(pd.Series([
            _term_value(row_terms, empirical, term)
            for row_terms, empirical in zip(assignments, empirical_ratios)
        ], index=df.index, name=col))
        terms[col] = {"task": term[0], "ratio": term[1]}
        counts[col] = counts[term]

    for prefix, rows in (("lag1", lag1), ("lag2", lag2)):
        lag_terms = [term for term in _collect_terms(rows) if sum(term in row for row in rows) >= min_count]
        for term in lag_terms:
            col = _col_name(prefix, term)
            parts.append(pd.Series([float(term in row) for row in rows], index=df.index, name=col))

    return pd.concat(parts, axis=1), counts, terms


def _empirical_ratios(df):
    mixes = [_empirical_mix(row) for _, row in df.iterrows()]
    control = [mix for mix, (_, row) in zip(mixes, df.iterrows()) if mix and not _assignments(row)]
    baseline = Counter()
    for mix in control or [mix for mix in mixes if mix]:
        baseline.update(mix)
    total = sum(baseline.values())
    baseline = {task: value / total for task, value in baseline.items()} if total else {}
    return [
        {
            task: share / baseline[task]
            for task, share in mix.items()
            if baseline.get(task, 0.0) > 0.0
        }
        for mix in mixes
    ]


def _empirical_mix(row):
    value = row.get("empirical_task_mix", None)
    if isinstance(value, dict):
        return {str(task): float(share) for task, share in value.items()}

    counts = {}
    for key, value in row.items():
        if str(key).startswith("kept_task/"):
            counts[str(key).split("/", 1)[1]] = float(value)
    total = sum(counts.values())
    return {task: count / total for task, count in counts.items()} if total else {}


def _term_value(row_terms, empirical, term):
    if term not in row_terms:
        return 0.0
    task, ratio = term
    if not empirical or float(ratio) == 1.0:
        return 1.0
    intended_delta = float(ratio) - 1.0
    if abs(intended_delta) < 1e-12:
        return 1.0
    realized_delta = float(empirical.get(task, 0.0)) - 1.0
    return realized_delta / intended_delta


def _assignments(row, lag=0):
    if lag:
        value = row.get(f"lag{lag}_active_task_ratios", None)
    else:
        value = row.get("active_task_ratios", None)
    if isinstance(value, dict):
        return {_term(task, ratio) for task, ratio in value.items() if float(ratio) != 1.0}

    task_key = f"lag{lag}_target_task" if lag else "target_task"
    ratio_key = f"lag{lag}_task_ratio" if lag else "task_ratio"
    drop_key = f"lag{lag}_drop_rate" if lag else "drop_rate"
    task = row.get(task_key, None)
    ratio = row.get(ratio_key, row.get(drop_key, None))
    if task in (None, "", "None") or pd.isna(task) or ratio is None or pd.isna(ratio):
        return set()
    return {_term(str(task), float(ratio))}


def _collect_terms(rows):
    return sorted({term for row in rows for term in row}, key=lambda x: (x[0], x[1]))


def _term(task, ratio):
    return (str(task), float(ratio))


def _col_name(prefix, term):
    task, ratio = term
    safe_task = str(task).replace("/", "_").replace(" ", "_")
    safe_ratio = ("%g" % float(ratio)).replace(".", "p").replace("-", "m")
    return f"{prefix}:{safe_task}:{safe_ratio}"


def _ols(y, x):
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    dof = max(1, x.shape[0] - np.linalg.matrix_rank(x))
    sigma2 = float(resid @ resid) / dof
    cov = sigma2 * np.linalg.pinv(x.T @ x)
    stderr = np.sqrt(np.maximum(np.diag(cov), 0.0))
    return beta, stderr


if __name__ == "__main__":
    main()
