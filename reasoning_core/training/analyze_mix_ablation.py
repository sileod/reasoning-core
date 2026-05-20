import argparse
import json

import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path")
    parser.add_argument("--step_df", type=int, default=2)
    args = parser.parse_args()

    result = analyze_log_path(args.log_path, step_df=args.step_df)
    print(format_recommendations(result))


def analyze_log_path(log_path, step_df=2):
    rows = load_rows(log_path)
    if not rows:
        raise ValueError(f"No rows found in {log_path}")
    return fit_recommendations(rows, step_df=step_df)


def load_rows(log_path):
    rows = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def fit_recommendations(rows, step_df=2):
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["eval_main_loss_delta", "eval_main_loss"]).copy()
    if df.empty:
        raise ValueError("No rows with eval_main_loss_delta and eval_main_loss")

    df["previous_loss"] = df["eval_main_loss"] - df["eval_main_loss_delta"]
    design = _build_design(df, step_df)
    y = df["eval_main_loss_delta"].to_numpy(dtype=float)

    beta, stderr = _ols(y, design.to_numpy(dtype=float))
    coef = pd.Series(beta, index=design.columns)
    se = pd.Series(stderr, index=design.columns)

    tasks = sorted(t for t in df["target_task"].dropna().unique() if str(t) not in ("", "None", "nan"))
    rates = sorted(float(r) for r in df["drop_rate"].dropna().unique())

    out = []
    for task in tasks:
        estimates = []
        for rate in rates:
            col = _term(task, rate)
            if col in coef:
                estimates.append((rate, coef[col], se[col]))
        if not estimates:
            continue
        best_rate, best_effect, best_se = min(estimates, key=lambda x: x[1])
        out.append({
            "task": task,
            "best_drop_rate": best_rate,
            "recommended_keep_ratio": 1.0 - best_rate,
            "stderr": best_se,
            "effect": best_effect,
        })

    result = pd.DataFrame(out)
    if result.empty:
        raise ValueError("No target_task x drop_rate terms found")
    result = result.sort_values(["recommended_keep_ratio", "task"], ascending=[False, True])
    return result


def format_recommendations(result):
    return result[["task", "best_drop_rate", "recommended_keep_ratio", "stderr"]].to_string(index=False)


def _build_design(df, step_df):
    parts = [
        pd.Series(1.0, index=df.index, name="intercept"),
        df["previous_loss"].astype(float).rename("previous_loss"),
    ]
    step = df["step"].astype(float)
    if step.nunique() > 1:
        x = (step - step.min()) / (step.max() - step.min())
        for degree in range(1, max(1, step_df) + 1):
            parts.append((x ** degree).rename(f"step_poly_{degree}"))

    for prefix, task_col, rate_col in [
        ("", "target_task", "drop_rate"),
        ("lag1_", "lag1_target_task", "lag1_drop_rate"),
        ("lag2_", "lag2_target_task", "lag2_drop_rate"),
    ]:
        if task_col not in df or rate_col not in df:
            continue
        for task, rate in sorted(set(zip(df[task_col], df[rate_col])), key=lambda x: str(x)):
            if pd.isna(task) or pd.isna(rate):
                continue
            name = prefix + _term(str(task), float(rate))
            parts.append(((df[task_col] == task) & (df[rate_col].astype(float) == float(rate))).astype(float).rename(name))

    return pd.concat(parts, axis=1)


def _ols(y, x):
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    dof = max(1, x.shape[0] - np.linalg.matrix_rank(x))
    sigma2 = float(resid @ resid) / dof
    cov = sigma2 * np.linalg.pinv(x.T @ x)
    stderr = np.sqrt(np.maximum(np.diag(cov), 0.0))
    return beta, stderr


def _term(task, rate):
    safe_task = str(task).replace("/", "_").replace(" ", "_")
    safe_rate = ("%g" % float(rate)).replace(".", "p")
    return f"target_task[{safe_task}]:drop_rate[{safe_rate}]"


if __name__ == "__main__":
    main()
