#!/usr/bin/env python
"""Run and summarize RC task influence measurements.

Influence runs consume a canonical TaskRow Parquet cache built by task_diagnostics.cache.
The runner trains the raw per-task influence kernel and rewrites a compact Markdown
ranking table (+ JSON sidecar). Gallery rendering lives in build_gallery.py.

Build changed/missing task rows:    python -m task_diagnostics.cache build --levels 0 1 2 --n 64
Run influence from those rows:      python task_diagnostics/task_influence.py --run-influence --taskrow-cache <cache_dir>
Rebuild the table from cache only:  python task_diagnostics/task_influence.py --no-local
"""

import argparse
import hashlib
import inspect
import json
import math
import os
import re
import shlex
import statistics as stats
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reasoning_core import get_task, list_tasks  # noqa: E402

SCRIPT_VERSION = 2
WEIGHT_PROFILES = {
    "dolci": {
        "dolci": 1.0,
        "bbh": 1.0,
        "fw": 1.0,
        "flan": 0.0,
    },
    "flan": {
        "flan": 1.0,
        "bbh": 1.0,
        "fw": 1.0,
        "dolci": 0.0,
    },
}
CONTRAST_WEIGHTS = {"flan": 1.0, "bbh": 1.0, "fw": 1.0}
TARGET_ALIASES = {"fineweb": "fw"}


def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and math.isfinite(x)]
    return sum(xs) / len(xs) if xs else float("nan")


def stdev(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and math.isfinite(x)]
    return stats.stdev(xs) if len(xs) > 1 else 0.0


def target_weight(weights, target):
    return weights.get(target, weights.get(TARGET_ALIASES.get(target, ""), 1.0))


def fmt(x, digits=3, signed=False):
    if x is None or not isinstance(x, (int, float)) or not math.isfinite(x):
        return ""
    sign = "+" if signed else ""
    return f"{x:{sign}.{digits}f}"


def load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:
        print(f"warning: failed to read {path}: {exc}", file=sys.stderr)
        return None


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def iso_time(ts):
    if not isinstance(ts, (int, float)) or not math.isfinite(ts):
        return ""
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def task_inventory(task_names):
    out = {}
    for name in task_names:
        try:
            task = get_task(name)
            source = Path(inspect.getfile(task.__class__)).resolve()
            rel_source = source.relative_to(ROOT) if source.is_relative_to(ROOT) else source
            mtime = source.stat().st_mtime
            out[name] = {
                "task": name,
                "category": task.category_name,
                "behavior_hash": task.behavior_hash(),
                "source_file": str(rel_source),
                "source_mtime": mtime,
                "source_modified": iso_time(mtime),
            }
        except Exception as exc:
            out[name] = {"task": name, "inventory_error": repr(exc)}
    return out


def cache_signature(task, samples):
    config = task.config.to_dict() if hasattr(task.config, "to_dict") else dict(task.config)
    return {
        "script_version": SCRIPT_VERSION,
        "task": task.task_name,
        "behavior_hash": task.behavior_hash(),
        "config": config,
        "samples": samples,
    }


def local_task_metrics(name, samples, refresh, cache):
    task = get_task(name)
    signature = cache_signature(task, samples)
    cache_key = f"{name}:{signature['behavior_hash']}:{samples}"
    record = cache.get(cache_key)
    if record and record.get("signature") == signature and not refresh:
        out = dict(record["metrics"])
        out["cache"] = "hit"
        return out

    started = time.time()
    out = {
        "task": name,
        "category": task.category_name,
        "behavior_hash": signature["behavior_hash"],
        "source_file": "",
        "source_modified": "",
        "ok": False,
        "cache": "miss",
    }
    try:
        source = Path(inspect.getfile(task.__class__)).resolve()
        rel_source = source.relative_to(ROOT) if source.is_relative_to(ROOT) else source
        out["source_file"] = str(rel_source)
        out["source_modified"] = iso_time(source.stat().st_mtime)
    except Exception:
        pass
    try:
        examples = task.validate(n_samples=samples, cache=True, refresh=refresh)
        prompt_tokens = [ex.metadata.get("_prompt_tokens") for ex in examples]
        answer_tokens = [ex.metadata.get("_answer_tokens") for ex in examples]
        gen_times = [ex.metadata.get("_time") for ex in examples]
        prompts = [ex.prompt for ex in examples]
        answers = [str(ex.answer) for ex in examples]
        out.update({
            "ok": True,
            "prompt_tokens_mean": mean(prompt_tokens),
            "answer_tokens_mean": mean(answer_tokens),
            "gen_time_mean": mean(gen_times),
            "prompt_unique_ratio": len(set(prompts)) / len(prompts) if prompts else float("nan"),
            "answer_unique_ratio": len(set(answers)) / len(answers) if answers else float("nan"),
            "elapsed": time.time() - started,
        })
    except Exception as exc:
        out.update({"error": repr(exc), "elapsed": time.time() - started})

    cache[cache_key] = {"signature": signature, "metrics": out}
    return out


def parse_result_tag(path, prefix):
    stem = Path(path).stem
    tag = stem[len(prefix):] if stem.startswith(prefix) else stem
    return tag.lstrip("_") or "canonical"


def result_files(results_dirs, prefix, include, exclude):
    paths = []
    for directory in results_dirs:
        d = Path(directory).expanduser()
        if d.exists():
            paths.extend(sorted(d.glob(f"{prefix}*.json")))
    if include:
        paths = [p for p in paths if any(s in p.name for s in include)]
    if exclude:
        paths = [p for p in paths if not any(s in p.name for s in exclude)]
    return paths


def collect_influence(paths):
    by_task = defaultdict(lambda: defaultdict(list))
    runs = []
    for path in paths:
        data = load_json(path)
        if not isinstance(data, dict) or not isinstance(data.get("tasks"), dict):
            continue
        tag = parse_result_tag(path, "influence")
        run_meta = {
            "file": str(path),
            "tag": tag,
            "seed": data.get("seed"),
            "train_steps": data.get("train_steps"),
            "main": data.get("main_data") or data.get("main"),
            "init": "scratch" if data.get("from_scratch") else "pretrained",
            "model": data.get("model"),
        }
        runs.append(run_meta)
        for task_name, rec in data["tasks"].items():
            if not isinstance(rec, dict):
                continue
            for key, value in rec.items():
                if not key.endswith("_delta") or not isinstance(value, (int, float)):
                    continue
                target = key[:-6]
                by_task[task_name][target].append({
                    "value": float(value),
                    "run": tag,
                    "file": path.name,
                })
    return by_task, runs


def collect_saturation(paths):
    by_task = defaultdict(lambda: defaultdict(list))
    runs = []
    for path in paths:
        data = load_json(path)
        if not isinstance(data, dict) or not isinstance(data.get("tasks"), dict):
            continue
        tag = parse_result_tag(path, "sat")
        runs.append({
            "file": str(path),
            "tag": tag,
            "seed": data.get("seed"),
            "train_steps": data.get("train_steps"),
            "main": data.get("main"),
            "init": data.get("init"),
        })
        for task_name, rec in data["tasks"].items():
            if not isinstance(rec, dict):
                continue
            acc0 = rec.get("acc0")
            accf = rec.get("acc_final")
            if isinstance(acc0, (int, float)) and isinstance(accf, (int, float)):
                by_task[task_name]["acc0"].append(float(acc0))
                by_task[task_name]["acc_final"].append(float(accf))
            for key in ("auc", "sat_step"):
                if isinstance(rec.get(key), (int, float)):
                    by_task[task_name][key].append(float(rec[key]))
    return by_task, runs


def aggregate_scores(task_names, influence, sat, weights):
    rows = {}
    targets = sorted({target for data in influence.values() for target in data})

    for task_name in task_names:
        row = {
            "task": task_name,
            "n_runs": 0,
            "influence_score": float("nan"),
            "targets": {},
            "sat": {},
        }
        terms = []
        for target in targets:
            vals = [x["value"] for x in influence.get(task_name, {}).get(target, [])]
            if not vals:
                continue
            w = target_weight(weights, target)
            delta = mean(vals)
            if w and math.isfinite(delta):
                terms.append((w, -delta))
            row["targets"][target] = {
                "mean": delta,
                "std": stdev(vals),
                "n": len(vals),
            }
            row["n_runs"] = max(row["n_runs"], len(vals))
        if terms:
            row["influence_score"] = sum(w * value for w, value in terms) / sum(w for w, _ in terms)
        for key, vals in sat.get(task_name, {}).items():
            row["sat"][key] = {"mean": mean(vals), "std": stdev(vals), "n": len(vals)}
        rows[task_name] = row
    return rows


def estimate_global_sigma(influence, weights, runs):
    """Global seed-noise sigma on influence_score: pooled cross-seed std of per-task scores.
    Only pools TRUE replicates — same config (model/main/steps/init), differing seed — so
    mixing configs or same-seed reruns doesn't fake a tiny sigma. Needs >=2 distinct seeds
    for a task at one config; None otherwise. z = score / sigma = effect in noise-sigmas."""
    meta = {r["tag"]: r for r in runs}
    def cfg(tag):
        m = meta.get(tag, {})
        return (m.get("model"), m.get("main"), m.get("train_steps"), m.get("init"))
    groups = defaultdict(lambda: defaultdict(dict))        # (task, config) -> seed -> {target: delta}
    for task, tdata in influence.items():
        for target, items in tdata.items():
            for it in items:
                groups[(task, cfg(it["run"]))][meta.get(it["run"], {}).get("seed")][target] = it["value"]
    variances = []
    for seeds in groups.values():
        scores = []
        for deltas in seeds.values():                     # one score per distinct seed
            terms = [(target_weight(weights, t), -d) for t, d in deltas.items() if target_weight(weights, t)]
            if terms:
                scores.append(sum(w * v for w, v in terms) / sum(w for w, _ in terms))
        if len(scores) >= 2:                              # >=2 distinct seeds at this config
            variances.append(stdev(scores) ** 2)
    return (sum(variances) / len(variances)) ** 0.5 if variances else None


def contrastive_scores(task_names, influence):
    rows = aggregate_scores(task_names, influence, {}, CONTRAST_WEIGHTS)
    return {name: rows[name]["influence_score"] for name in rows}


def parse_weights(profile, raw):
    weights = dict(WEIGHT_PROFILES[profile])
    for item in raw or []:
        if "=" not in item:
            raise SystemExit(f"bad --weight {item!r}; expected target=value")
        key, value = item.split("=", 1)
        weights[key.strip()] = float(value)
    return weights


def markdown_table(rows, columns):
    out = []
    out.append("| " + " | ".join(columns) + " |")
    out.append("|" + "|".join("---" for _ in columns) + "|")
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def write_machine_outputs(json_path, records, influence_runs, sat_runs, contrast_runs, args):
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script_version": SCRIPT_VERSION,
        "profile": args.profile,
        "weights": args.weights,
        "records": records,
        "influence_runs": influence_runs,
        "contrastive_runs": contrast_runs,
        "saturation_runs": sat_runs,
    }
    write_json(json_path, payload)


def build_records(local, inventory, scores, contrastive_scores=None, global_sigma=None):
    contrastive_scores = contrastive_scores or {}
    local_by_task = {r["task"]: r for r in local}
    ranked = sorted(
        scores.values(),
        key=lambda r: (
            math.inf if not math.isfinite(r["influence_score"]) else -r["influence_score"],
            r["task"],
        ),
    )
    records = []
    for rank, row in enumerate(ranked, 1):
        loc = local_by_task.get(row["task"], {})
        inv = inventory.get(row["task"], {})
        sat = row["sat"]
        rec = {
            "rank": rank,
            "task": row["task"],
            "category": loc.get("category") or inv.get("category", ""),
            "influence_score": row["influence_score"],
            "z": (row["influence_score"] / global_sigma
                  if global_sigma and math.isfinite(row["influence_score"]) else None),
            "n_runs": row["n_runs"],
            "contrastive_score": contrastive_scores.get(row["task"]),
            "behavior_hash": loc.get("behavior_hash") or inv.get("behavior_hash", ""),
            "source_file": loc.get("source_file") or inv.get("source_file", ""),
            "source_modified": loc.get("source_modified") or inv.get("source_modified", ""),
            "ok": loc.get("ok", ""),
            "issue": "" if loc.get("ok") or loc.get("ok") is None else loc.get("error", "not checked"),
            "prompt_tokens_mean": loc.get("prompt_tokens_mean"),
            "answer_tokens_mean": loc.get("answer_tokens_mean"),
            "targets": row["targets"],
            "saturation": row["sat"],
        }
        for target in ("flan", "fw", "bbh", "dolci"):
            rec[f"{target}_delta"] = row["targets"].get(target, {}).get("mean")
        if rec.get("fw_delta") is None:
            rec["fw_delta"] = row["targets"].get("fineweb", {}).get("mean")
        rec["acc_start"] = sat.get("acc0", {}).get("mean")
        rec["acc_end"] = sat.get("acc_final", {}).get("mean")
        records.append(rec)
    return records


def write_markdown(path, records, influence_runs, sat_runs, contrast_runs, args):
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Task Influence",
        "",
        f"Updated: {generated}",
        "",
        "Lower delta means the task reduced held-out loss versus the baseline. "
        "`influence_score` is the weighted mean of `-delta`, so positive means the "
        "task helped on the weighted targets. Default target weights: "
        + ", ".join(f"{k}={v:g}" for k, v in sorted(args.weights.items())),
        "",
        f"Profile: `{args.profile}`.",
        "",
        f"Influence files: {len(influence_runs)}. Saturation files: {len(sat_runs)}. "
        f"Contrastive influence files: {len(contrast_runs)}. "
        f"Local task checks: {sum(1 for r in records if r.get('ok'))}/{sum(1 for r in records if r.get('ok') != '')} ok.",
        "",
        "Saturation accuracy is diagnostic and is not part of the score.",
        "",
    ]

    # Compact ranking: real tasks only (skip mixture/experiment artifacts), the three
    # scored deltas + merged tok/acc diagnostics. flan + full detail live in the JSON sidecar.
    # Allow into the table: all registered tasks, anything explicitly named via --tasks
    # (naming a DevTask is enough — no --include-dev needed), and the --include-dev allowlist
    # (for sweeps where DevTasks arrive via the influence files rather than --tasks).
    registered = (set(list_tasks())
                  | set(getattr(args, "tasks", None) or [])
                  | set(getattr(args, "include_dev", []) or []))

    def _pair(a, b, digits, sep):
        sa, sb = fmt(a, digits), fmt(b, digits)
        return f"{sa}{sep}{sb}" if (sa or sb) else ""

    rows = []
    for row in records:
        if row["task"] not in registered:
            continue
        rows.append([
            str(len(rows) + 1),
            row["task"],
            fmt(row["influence_score"], 2, signed=True),
            fmt(row.get("z"), 1, signed=True),
            fmt(row.get("dolci_delta"), 4, signed=True),
            fmt(row.get("bbh_delta"), 3, signed=True),
            fmt(row.get("fw_delta"), 4, signed=True),
            _pair(row.get("prompt_tokens_mean"), row.get("answer_tokens_mean"), 0, "/"),
            _pair(row.get("acc_start"), row.get("acc_end"), 2, "→"),
            (row.get("behavior_hash", "") or "")[:7],
        ])

    lines.append("## Ranking")
    lines.append("")
    sigma = getattr(args, "global_sigma", None)
    zline = (f" `z` = score / global seed-noise σ={sigma:.3f} (|z|≳2 ⇒ effect exceeds seed noise);"
             if sigma else " `z` needs ≥2 seeds (run more --seed replicates) — blank until then;")
    lines.append("Arrows mark the good direction: `score ↑` (higher = better helper); the deltas "
                 "`↓` (lower = reduced held-out loss = helped)." + zline + " `tok` = prompt/answer "
                 "tokens, `acc` = start→end (both diagnostic). flan delta is in the JSON sidecar.")
    lines.append("")
    lines.append(markdown_table(rows, [
        "#", "task", "score ↑", "z ↑", "dolci ↓", "bbh ↓", "fw ↓", "tok", "acc", "hash",
    ]))
    lines.append("")

    issues = [(r["task"], str(r.get("issue", ""))[:120]) for r in records
              if not (r.get("ok") or r.get("ok") is None) and r.get("issue")]
    if issues:
        lines.append("## Issues")
        lines.append("")
        for task, issue in issues:
            lines.append(f"- `{task}`: {issue}")
        lines.append("")

    lines.append(f"_Inputs: {len(influence_runs)} influence + {len(sat_runs)} saturation"
                 + (f" + {len(contrast_runs)} contrastive" if contrast_runs else "")
                 + " result file(s). Full per-target detail and diagnostics in the JSON sidecar._")
    lines.append("")

    md = "\n".join(lines) + "\n"
    if path is not None:                     # path=None (dry-run): return text, write nothing
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(md)
    return md


def default_results_dirs():
    return [ROOT / "per_task_results"]


def clean_run_tag(tag):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(tag).strip().lstrip("_"))


def run_hash(task_names, args):
    inventory = task_inventory(task_names)
    payload = {
        "tasks": task_names,
        "hashes": {name: inventory.get(name, {}).get("behavior_hash", "") for name in task_names},
        "model": args.model,                 # distinct tag per model (else runs collide across models)
        "main_data": args.main_data,
        "seed": args.seed,
        "train_steps": args.train_steps,
        "mix_aux": args.mix_aux,
        "taskrow_cache": taskrow_cache_sig(args.taskrow_cache),
    }
    return hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:10]


def taskrow_cache_sig(path):
    if not path:
        return ""
    p = Path(path).expanduser()
    manifest = load_json(p / "manifest.json")
    if isinstance(manifest, dict):
        return manifest.get("cache_id") or hashlib.sha1(json.dumps(manifest, sort_keys=True).encode()).hexdigest()[:12]
    return str(p)


def run_init_tag(args):
    return "scratch" if args.from_scratch_bool else "pretrained"


def runner_results_dir(args):
    base = Path(args.run_workdir).expanduser() if args.run_workdir else ROOT
    subdir = "per_task_results_rgym" if args.aux_dataset == "rgym" else "per_task_results"
    return base / subdir


def run_result_paths(args):
    mix = int(args.mix_aux * 100)
    suffix = (
        f"_{args.run_tag}_S{args.seed}_T{args.train_steps}_M{mix}_"
        f"{args.main_data}_{run_init_tag(args)}.json"
    )
    root = runner_results_dir(args)
    return root / f"influence{suffix}", root / f"sat{suffix}"


def completed_result(path, task_names):
    data = load_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), dict):
        return False
    return all(name in data["tasks"] for name in task_names)


def launch_influence_run(args, task_names):
    runner = Path(args.runner).expanduser()
    if not runner.exists():
        raise SystemExit(f"--runner does not exist: {runner}")
    workdir = Path(args.run_workdir).expanduser() if args.run_workdir else ROOT
    if not workdir.exists():
        raise SystemExit(f"--run-workdir does not exist: {workdir}")
    if not args.taskrow_cache:
        raise SystemExit("--run-influence requires --taskrow-cache. Build one with `python -m task_diagnostics.cache build`.")

    args.run_tag = clean_run_tag(args.run_tag or f"LOCAL_{run_hash(task_names, args)}")
    cache_path = Path(args.taskrow_cache).expanduser()
    if not cache_path.exists():
        raise SystemExit(f"--taskrow-cache does not exist: {cache_path}")
    print(f"TaskRow cache: {cache_path}")

    influence_path, sat_path = run_result_paths(args)
    if completed_result(influence_path, task_names) and not args.force_run:
        print(f"influence cache fresh: {influence_path}")
        return {"launched": False, "influence": influence_path, "sat": sat_path}

    log_path = Path(args.run_log).expanduser() if args.run_log else ROOT / "task_influence_work" / f"{args.run_tag}.log"
    script_path = ROOT / "task_influence_work" / f"run_{args.run_tag}.sh"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.parent.mkdir(parents=True, exist_ok=True)
    env = {
        "RUN_TAG": args.run_tag,
        "TASKROW_CACHE": str(cache_path),
        "OUT_DIR": str(runner_results_dir(args)),
        "AUX_DATASET": args.aux_dataset,
        "MODEL": args.model,
        "BATCH": str(args.batch),
        "GRAD_ACCUM": str(args.grad_accum),
        "MAIN_DATA": args.main_data,
        "FROM_SCRATCH": "1" if args.from_scratch_bool else "0",
        "SEED": str(args.seed),
        "TRAIN_STEPS": str(args.train_steps),
        "MIX_AUX": str(args.mix_aux),
        "COMPLETION_ONLY": "1" if args.completion_only else "0",
        "EVAL_FLAN": "0" if args.no_eval_flan else "1",
        "LOG_SAT": "1",
        "SAT_EVERY": str(args.sat_every),
        "TASKS": ",".join(task_names),
    }
    exports = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())
    script_path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"cd {shlex.quote(str(workdir))}\n"
        f"{exports} python {shlex.quote(str(runner))} 2>&1 | tee {shlex.quote(str(log_path))}\n",
        encoding="utf-8",
    )
    script_path.chmod(0o755)

    if args.foreground:
        subprocess.run(["bash", str(script_path)], check=True)
    else:
        session = clean_run_tag(args.tmux_session or f"rc_influence_{args.run_tag.lower()}")[:80]
        subprocess.run(["tmux", "new-session", "-d", "-s", session, "bash", str(script_path)], check=True)
        print(f"launched tmux: {session}")
        print(f"log: {log_path}")
        print(f"expected: {influence_path}")
    return {"launched": not args.foreground, "influence": influence_path, "sat": sat_path}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="task_diagnostics/TASK_INFLUENCE_RESULTS.md")
    parser.add_argument("--cache", default=".task_influence_cache.json")
    parser.add_argument("--json-out", default=None,
                        help="Machine-readable JSON output. Default: --out with .json suffix.")
    parser.add_argument("--taskrow-cache", default=None,
                        help="Use a canonical TaskRow Parquet cache for aux, saturation, and reward rows.")
    parser.add_argument("--results-dir", action="append", default=None,
                        help="Directory with influence_*.json and sat_*.json. Can repeat.")
    parser.add_argument("--include", action="append", default=[],
                        help="Only use result files whose filename contains this string. Can repeat.")
    parser.add_argument("--contrastive-include", action="append", default=["CONTRAST"],
                        help="Filename substring(s) for contrastive influence files.")
    parser.add_argument("--exclude", action="append", default=[],
                        help="Skip result files whose filename contains this string. Can repeat.")
    parser.add_argument("--tasks", nargs="*", default=None)
    parser.add_argument("--include-dev", nargs="*", default=[],
                        help="DevTask names to allow into the ranking table (they are excluded by "
                             "default since list_tasks() omits DevTasks). e.g. rocq_compute_nf.")
    parser.add_argument("--samples", type=int, default=4,
                        help="Validation samples per task for local generator metrics.")
    parser.add_argument("--refresh", action="store_true",
                        help="Recompute local metrics even when task behavior hashes match.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Render the table to stdout without writing the .md/.json (report-only).")
    parser.add_argument("--no-local", action="store_true",
                        help="Skip local task generation/validation and only aggregate result JSONs.")
    parser.add_argument("--weight", action="append", default=[],
                        help="Override target score weight, e.g. --weight flan=3 --weight fw=0.5")
    parser.add_argument("--profile", choices=sorted(WEIGHT_PROFILES), default="dolci",
                        help="Named scoring profile. --weight overrides individual values.")
    parser.add_argument("--run-influence", action="store_true",
                        help="Build/reuse aux data and launch the raw per-task influence trainer.")
    parser.add_argument("--runner", default=str(ROOT / "task_diagnostics" / "per_task_influence.py"),
                        help="Path to the vendored per_task_influence.py trainer.")
    parser.add_argument("--run-workdir", default=None,
                        help="Working directory for --runner. Default: repo root.")
    parser.add_argument("--run-tag", default=None,
                        help="RUN_TAG for raw result files. Default: LOCAL_<task/config hash>.")
    parser.add_argument("--run-log", default=None,
                        help="Log path for --run-influence. Default: task_influence_work/<tag>.log.")
    parser.add_argument("--tmux-session", default=None,
                        help="tmux session name for background --run-influence.")
    parser.add_argument("--foreground", action="store_true",
                        help="Run influence trainer in the current process instead of tmux.")
    parser.add_argument("--force-run", action="store_true",
                        help="Rerun raw influence even if the expected result file is complete.")
    parser.add_argument("--aux-dataset", choices=("rc", "rgym", "basic"), default="rc")
    parser.add_argument("--main-data", choices=("dolci", "flan", "fw", "fw_recent", "tasksource",
                                                "fwdolci", "fwtasksource", "codealpaca", "fwdolcicode"), default="dolci")
    parser.add_argument("--model", dest="models", nargs="+", default=["HuggingFaceTB/SmolLM2-135M"],
                        help="One or more decoder models; each runs separately with a distinct "
                             "model-specific tag/file (compare models from their per-model JSON).")
    parser.add_argument("--seed", type=int, default=43)
    parser.add_argument("--train-steps", type=int, default=300)
    parser.add_argument("--mix-aux", type=float, default=0.2)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--grad-accum", type=int, default=1)
    parser.add_argument("--from-scratch", choices=("0", "1"), default="0")
    parser.add_argument("--completion-only", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--no-eval-flan", action="store_true")
    parser.add_argument("--sat-every", type=int, default=50)
    return parser.parse_args()


def main():
    args = parse_args()
    args.weights = parse_weights(args.profile, args.weight)
    args.from_scratch_bool = args.from_scratch == "1"
    task_names = args.tasks or list_tasks()
    results_dirs = [Path(p).expanduser() for p in (args.results_dir or default_results_dirs())]

    run_info = None
    if args.run_influence:
        run_tags, launched = [], False
        for m in args.models:                     # one influence run per model (distinct tag/file)
            args.model = m
            run_info = launch_influence_run(args, task_names)
            run_tags.append(args.run_tag)
            run_dir = runner_results_dir(args)
            if run_dir not in results_dirs:
                results_dirs.insert(0, run_dir)
            launched = launched or (run_info.get("launched") and not args.foreground)
        if launched:
            print("raw influence run(s) in progress; rerun this command after they complete to refresh the report")
            return
        if len(args.models) > 1:                  # combined table would conflate models -> report per-model files
            print("multi-model run complete; refresh a per-model table with --no-local and one --include tag:")
            for t in run_tags:
                print(f"  --include {t}")
            return
        if not args.include:
            args.include = run_tags

    cache = load_json(args.cache) if Path(args.cache).exists() else {}
    if not isinstance(cache, dict):
        cache = {}

    local = []
    if args.no_local:
        for name in task_names:
            local.append({"task": name, "ok": None})
    else:
        for name in task_names:
            print(f"local {name}", flush=True)
            local.append(local_task_metrics(name, args.samples, args.refresh, cache))
        write_json(args.cache, cache)

    contrast_paths = result_files(results_dirs, "influence", args.contrastive_include, args.exclude)
    contrast_names = {p.name for p in contrast_paths}
    influence_paths = [
        p for p in result_files(results_dirs, "influence", args.include, args.exclude)
        if p.name not in contrast_names
    ]
    sat_paths = result_files(results_dirs, "sat", args.include, args.exclude)
    influence, influence_runs = collect_influence(influence_paths)
    contrastive, contrast_runs = collect_influence(contrast_paths)
    saturation, sat_runs = collect_saturation(sat_paths)

    all_names = task_names if args.tasks else sorted(set(task_names) | set(influence) | set(saturation))
    inventory = task_inventory(all_names)
    scores = aggregate_scores(all_names, influence, saturation, args.weights)
    c_scores = contrastive_scores(all_names, contrastive)
    args.global_sigma = estimate_global_sigma(influence, args.weights, influence_runs)   # seed noise from replicates
    records = build_records(local, inventory, scores, c_scores, args.global_sigma)
    json_out = args.json_out or str(Path(args.out).with_suffix(".json"))
    if args.dry_run:                          # render + print, touch no files
        print(write_markdown(None, records, influence_runs, sat_runs, contrast_runs, args))
        print(f"[dry-run] would write {args.out} and {json_out}")
        return
    write_markdown(args.out, records, influence_runs, sat_runs, contrast_runs, args)
    write_machine_outputs(json_out, records, influence_runs, sat_runs, contrast_runs, args)

    print(f"wrote {args.out}")
    print(f"wrote {json_out}")
    for row in records[:12]:
        print(
            f"{row['task']:<32} influence={fmt(row['influence_score'], 3, True):>8} "
            f"flan={fmt(row.get('flan_delta'), 4, True):>9} "
            f"fw={fmt(row.get('fw_delta'), 4, True):>9} "
            f"acc={fmt(row.get('acc_start'), 3):>5}->{fmt(row.get('acc_end'), 3):<5}"
        )


if __name__ == "__main__":
    main()
