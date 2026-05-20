import argparse
import json

import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path")
    parser.add_argument("--step_df", type=int, default=2)
    parser.add_argument("--unit_col", type=str, default="auto")
    args = parser.parse_args()

    result = analyze_log_path(args.log_path, step_df=args.step_df, unit_col=args.unit_col)
    print(format_recommendations(result))


def analyze_log_path(log_path, step_df=2, unit_col="auto"):
    rows = load_rows(log_path)
    if not rows:
        raise ValueError(f"No rows found in {log_path}")
    return fit_recommendations(rows, step_df=step_df, unit_col=unit_col)


def load_rows(log_path):
    rows = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def fit_recommendations(rows, step_df=2, unit_col="auto"):
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["eval_main_loss_delta", "eval_main_loss"]).copy()
    if df.empty:
        raise ValueError("No rows with eval_main_loss_delta and eval_main_loss")

    unit_cols = _resolve_unit_columns(df, unit_col)
    df["previous_loss"] = df["eval_main_loss"] - df["eval_main_loss_delta"]
    design = _build_design(df, step_df, unit_cols)
    y = df["eval_main_loss_delta"].to_numpy(dtype=float)

    beta, stderr = _ols(y, design.to_numpy(dtype=float))
    coef = pd.Series(beta, index=design.columns)
    se = pd.Series(stderr, index=design.columns)

    groups = sorted(
        g for g in df[unit_cols[0][1]].dropna().unique()
        if str(g) not in ("", "None", "nan")
    )
    rates = sorted(float(r) for r in df["drop_rate"].dropna().unique())

    out = []
    for group in groups:
        estimates = []
        for rate in rates:
            col = _term(group, rate)
            if col in coef:
                estimates.append((rate, coef[col], se[col]))
        if not estimates:
            continue
        best_rate, best_effect, best_se = min(estimates, key=lambda x: x[1])
        out.append({
            "unit": group,
            "best_drop_rate": best_rate,
            "recommended_keep_ratio": 1.0 - best_rate,
            "stderr": best_se,
            "effect": best_effect,
        })

    result = pd.DataFrame(out)
    if result.empty:
        raise ValueError("No target unit x drop_rate terms found")
    result = result.sort_values(["recommended_keep_ratio", "unit"], ascending=[False, True])
    return result


def format_recommendations(result):
    return result[["unit", "best_drop_rate", "recommended_keep_ratio", "stderr"]].to_string(index=False)


def _build_design(df, step_df, unit_cols):
    parts = [
        pd.Series(1.0, index=df.index, name="intercept"),
        df["previous_loss"].astype(float).rename("previous_loss"),
    ]
    step = df["step"].astype(float)
    if step.nunique() > 1:
        x = (step - step.min()) / (step.max() - step.min())
        for degree in range(1, max(1, step_df) + 1):
            parts.append((x ** degree).rename(f"step_poly_{degree}"))

    for prefix, unit_column, rate_col in unit_cols:
        if unit_column not in df or rate_col not in df:
            continue
        for unit, rate in sorted(set(zip(df[unit_column], df[rate_col])), key=lambda x: str(x)):
            if pd.isna(unit) or pd.isna(rate):
                continue
            name = prefix + _term(str(unit), float(rate))
            parts.append(((df[unit_column] == unit) & (df[rate_col].astype(float) == float(rate))).astype(float).rename(name))

    return pd.concat(parts, axis=1)


def _resolve_unit_columns(df, unit_col):
    if unit_col == "auto":
        base = "target_unit" if "target_unit" in df else "target_group"
    else:
        base = unit_col
    return [
        ("", base, "drop_rate"),
        ("lag1_", f"lag1_{base}", "lag1_drop_rate"),
        ("lag2_", f"lag2_{base}", "lag2_drop_rate"),
    ]


def _ols(y, x):
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    dof = max(1, x.shape[0] - np.linalg.matrix_rank(x))
    sigma2 = float(resid @ resid) / dof
    cov = sigma2 * np.linalg.pinv(x.T @ x)
    stderr = np.sqrt(np.maximum(np.diag(cov), 0.0))
    return beta, stderr


def _term(group, rate):
    safe_group = str(group).replace("/", "_").replace(" ", "_")
    safe_rate = ("%g" % float(rate)).replace(".", "p")
    return f"target_group[{safe_group}]:drop_rate[{safe_rate}]"


if __name__ == "__main__":
    main()
