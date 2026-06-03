import argparse
import hashlib
import json
import shlex
import subprocess
from pathlib import Path

from huggingface_hub import dataset_info, hf_hub_url


DEFAULT_MAIN_DATA = ("dolci", "fw")
DATA_MAP = {
    "rc": "reasoning-core/procedural-pretraining-pile",
    "rg": "reasoning-core/reasoning-gym",
}
DEFAULT_METRICS = (
    "eval_main_loss",
    "nll/folio/nll",
    "nll/leaderboard_bbh/nll",
)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name in ("plan", "run"):
        p = sub.add_parser(name)
        add_grid_args(p)
        p.add_argument("--python", default="python")
        p.add_argument("--reasoning-core-path", default=str(Path(__file__).resolve().parents[2]))
        p.add_argument("--run-sft", default="")
        p.add_argument("--state-dir", default="checkpoints/task_importance")
        p.add_argument("--rerun", action="store_true")
        p.add_argument("--extra", nargs=argparse.REMAINDER, default=[])

    p = sub.add_parser("summary")
    p.add_argument("--experiment-name", required=True)
    p.add_argument("--checkpoints", default="checkpoints")
    p.add_argument("--metrics", nargs="*", default=list(DEFAULT_METRICS))

    args = parser.parse_args()
    if args.cmd == "summary":
        summarize(args)
        return

    commands = build_commands(args)
    if args.cmd == "plan":
        for command in commands:
            print(" ".join(shlex.quote(x) for x in command))
        return

    state_path = Path(args.state_dir) / f"{args.experiment_name}.json"
    state = {} if args.rerun else _read_state(state_path)
    for i, command in enumerate(commands, start=1):
        key = _command_key(command)
        if state.get(key, {}).get("status") == "done":
            print(f"[{i}/{len(commands)}] skip done {state[key].get('label', key)}", flush=True)
            continue
        print(f"[{i}/{len(commands)}] {' '.join(shlex.quote(x) for x in command)}", flush=True)
        subprocess.run(command, check=True)
        state[key] = {"status": "done", "label": _label(command), "command": command}
        _write_state(state_path, state)


def add_grid_args(parser):
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--main-data", nargs="*", default=list(DEFAULT_MAIN_DATA), choices=("dolci", "fw"))
    parser.add_argument("--aux-data", default="rc")
    parser.add_argument("--aux-mode", default="")
    parser.add_argument("--aux-level", default="")
    parser.add_argument("--seeds", nargs="*", type=int, default=[1, 2])
    parser.add_argument("--tasks", nargs="*", default=None)
    parser.add_argument("--token-budget", default="5M")
    parser.add_argument("--aux-ratio", default="0.7")
    parser.add_argument("--include-main-only", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-full-mix", action=argparse.BooleanOptionalAction, default=False)


def build_commands(args):
    root = Path(args.reasoning_core_path).expanduser().resolve()
    run_sft = Path(args.run_sft).expanduser() if args.run_sft else root / "reasoning_core/training/run_sft.py"
    if not run_sft.is_absolute():
        run_sft = root / run_sft
    tasks = args.tasks if args.tasks is not None else remote_tasks(args.aux_data)
    treatments = []
    if args.include_main_only:
        treatments.append(("none", "0", ""))
    if args.include_full_mix:
        treatments.append(("all", args.aux_ratio, ""))
    treatments.extend((task, args.aux_ratio, task) for task in tasks)

    commands = []
    for main_data in args.main_data:
        for seed in args.seeds:
            for treatment, aux_ratio, aux_task in treatments:
                command = [
                    args.python,
                    str(run_sft),
                    "--experiment_name", args.experiment_name,
                    "--main_data", main_data,
                    "--aux_data", args.aux_data,
                    "--aux_ratio", str(aux_ratio),
                    "--seed", str(seed),
                    "--token_budget", str(args.token_budget),
                ]
                if aux_task:
                    command += ["--aux_task", aux_task]
                if args.aux_mode:
                    command += ["--aux_mode", args.aux_mode]
                if args.aux_level:
                    command += ["--aux_level", args.aux_level]
                command += list(args.extra)
                commands.append(command)
    return commands


def summarize(args):
    rows = []
    for meta_path in Path(args.checkpoints).glob("*/metrics.meta.json"):
        run_dir = meta_path.parent
        metrics_path = run_dir / "metrics.jsonl"
        if not metrics_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        cfg = meta.get("args", {})
        if cfg.get("experiment_name") != args.experiment_name:
            continue
        treatment = _treatment(cfg)
        values = _last_metrics(metrics_path, args.metrics)
        for metric, value in values.items():
            rows.append({
                "run_hash": meta.get("run_hash"),
                "main_data": cfg.get("main_data"),
                "seed": cfg.get("seed"),
                "treatment": treatment,
                "metric": metric,
                "value": value,
            })

    if not rows:
        print("No matching local metrics found.")
        return

    try:
        import pandas as pd
    except ImportError:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return

    df = pd.DataFrame(rows)
    base = df[df.treatment == "none"].rename(columns={"value": "baseline"})
    joined = df.merge(
        base[["main_data", "seed", "metric", "baseline"]],
        on=["main_data", "seed", "metric"],
        how="left",
    )
    joined["delta_vs_none"] = joined["value"] - joined["baseline"]
    out = (
        joined[joined.treatment != "none"]
        .groupby(["main_data", "treatment", "metric"], dropna=False)
        .agg(
            value_mean=("value", "mean"),
            delta_mean=("delta_vs_none", "mean"),
            delta_std=("delta_vs_none", "std"),
            n=("delta_vs_none", "count"),
        )
        .reset_index()
    )
    out["delta_se"] = out["delta_std"] / out["n"].pow(0.5)
    print(out.sort_values(["metric", "main_data", "delta_mean"]).to_string(index=False))


def _last_metrics(path, wanted):
    wanted = set(wanted)
    values = {}
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            metrics = row.get("metrics", {})
            if row.get("kind") == "eval_main":
                for key in ("loss", "main_loss"):
                    if "eval_main_loss" in wanted and key in metrics:
                        values["eval_main_loss"] = metrics[key]
            if row.get("kind") == "downstream":
                for key in wanted:
                    if key in metrics:
                        values[key] = metrics[key]
    return values


def _treatment(cfg):
    if float(cfg.get("aux_ratio", 0) or 0) <= 0:
        return "none"
    return cfg.get("aux_task") or "all"


def _default_tasks():
    from reasoning_core import list_tasks

    return list_tasks()


def remote_tasks(aux_data, cache_dir="checkpoints/task_importance"):
    dataset = DATA_MAP.get(aux_data, aux_data)
    info = dataset_info(dataset, files_metadata=True)
    cache = Path(cache_dir) / f"tasks-{_safe_name(dataset)}-{info.sha[:8]}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    try:
        tasks = _tasks_from_test_parquet(dataset, info)
    except Exception as exc:
        if aux_data == "rc":
            print(f"Remote task discovery failed for {dataset}: {exc}; falling back to local list_tasks().")
            tasks = _default_tasks()
        else:
            raise
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(tasks, indent=2, sort_keys=True))
    return tasks


def _tasks_from_test_parquet(dataset, info):
    import fsspec
    import pyarrow.parquet as pq

    test_files = sorted(
        s.rfilename for s in info.siblings
        if s.rfilename.endswith(".parquet") and "/test-" in s.rfilename
    )
    if not test_files:
        raise ValueError(f"No test parquet files found for {dataset}")

    tasks = set()
    metadata_values = []
    fs = fsspec.filesystem("https")
    for filename in test_files:
        url = hf_hub_url(dataset, filename, repo_type="dataset")
        with fs.open(url, "rb") as f:
            table = pq.read_table(f, columns=["task", "metadata"])
        if "task" in table.column_names:
            tasks.update(str(x) for x in table.column("task").unique().to_pylist() if x)
        if "metadata" in table.column_names:
            metadata_values.extend(table.column("metadata").to_pylist())

    if len(tasks) <= 1 and metadata_values:
        source_tasks = set()
        for raw in metadata_values:
            meta = _json_dict(raw)
            value = meta.get("source_dataset") or meta.get("task_name") or meta.get("rg_task")
            if value:
                source_tasks.add(str(value))
        if source_tasks:
            tasks = source_tasks
    return sorted(tasks)


def _json_dict(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            value = json.loads(raw)
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _safe_name(value):
    return str(value).replace("/", "_").replace(":", "_")


def _command_key(command):
    return hashlib.sha256(json.dumps(command, sort_keys=True).encode()).hexdigest()[:16]


def _label(command):
    values = {}
    for i, token in enumerate(command[:-1]):
        if token.startswith("--"):
            values[token[2:]] = command[i + 1]
    task = values.get("aux_task") or ("none" if values.get("aux_ratio") == "0" else "all")
    mode = values.get("aux_mode") or "all"
    level = values.get("aux_level") or "all"
    return f"{values.get('main_data')}:{values.get('seed')}:{task}:{mode}:{level}"


def _read_state(path):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(path)


if __name__ == "__main__":
    main()
