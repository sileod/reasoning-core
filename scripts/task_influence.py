#!/usr/bin/env python
"""Run and summarize RC task influence measurements.

Builds aux data — either generated locally from task generators (--source generate,
default) or pulled from a pre-built HF staging repo (--source staging) — launches the
raw influence trainer for tasks whose behavior hash changed, and rewrites a compact
Markdown ranking table (+ JSON sidecar). Gallery rendering lives in build_gallery.py.

Refresh everything that changed:   python scripts/task_influence.py --run-influence
Pull staging instead of gen:       python scripts/task_influence.py --run-influence --source staging
Rebuild the table from cache only:  python scripts/task_influence.py --no-local
"""

import argparse
import hashlib
import inspect
import json
import math
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


def _verification_rows(task, examples, limit):
    pool = [str(ex.answer) for ex in examples]
    rows, yes, no = [], 0, 0
    for i, ex in enumerate(examples):
        prompt, answer = ex.prompt, str(ex.answer)
        want_yes = yes <= no
        if want_yes:
            candidate, label = answer, "Yes"
        else:
            order = sorted(
                range(len(pool)),
                key=lambda j: hashlib.sha1(f"{prompt}\0{j}".encode()).hexdigest(),
            )
            candidate = None
            for j in order:
                cand = pool[j]
                if cand == answer:
                    continue
                try:
                    if float(task.score_answer(cand, ex)) != 1.0:
                        candidate = cand
                        break
                except Exception:
                    if cand != answer:
                        candidate = cand
                        break
            if candidate is None:
                continue
            label = "No"
        rows.append([f"{prompt}\nAnswer:\n{candidate}\nCorrect? (Yes/No)", label])
        yes += label == "Yes"
        no += label == "No"
        if len(rows) >= limit:
            break
    return rows


def build_aux_data(path, task_names, examples_per_task, levels, max_tokens, refresh, aux_mode,
                   dedup=True):
    """Build LOCAL_AUX JSON keyed as task -> [[prompt, completion], ...] from local generators."""
    path = Path(path)
    data = {}
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script_version": SCRIPT_VERSION,
        "source": "generate",
        "dedup": dedup,
        "examples_per_task": examples_per_task,
        "levels": levels,
        "max_tokens": max_tokens,
        "aux_mode": aux_mode,
        "tasks": {},
    }
    for name in task_names:
        print(f"aux {name}", flush=True)
        task = get_task(name)
        source = Path(inspect.getfile(task.__class__)).resolve()
        rel = source.relative_to(ROOT) if source.is_relative_to(ROOT) else source
        examples_all, seen = [], set()
        per_level = max(1, math.ceil(examples_per_task / max(1, len(levels))))
        want = examples_per_task * (2 if aux_mode == "contrastive" else 1)
        for level in levels:
            examples = task.generate_balanced_batch(
                batch_size=per_level,
                max_tokens=max_tokens,
                level=level,
            )
            for ex in examples:
                if len(examples_all) >= want:
                    break
                if max_tokens:
                    pt = ex.metadata.get("_prompt_tokens", 0) or 0
                    at = ex.metadata.get("_answer_tokens", 0) or 0
                    if pt + at > max_tokens:
                        continue
                if dedup:
                    if ex.prompt in seen:
                        continue
                    seen.add(ex.prompt)
                examples_all.append(ex)
            if len(examples_all) >= want:
                break
        if aux_mode == "contrastive":
            rows = _verification_rows(task, examples_all, examples_per_task)
        else:
            rows = [[ex.prompt, str(ex.answer)] for ex in examples_all[:examples_per_task]]
        data[name] = rows
        manifest["tasks"][name] = {
            "n": len(rows),
            "behavior_hash": task.behavior_hash(),
            "source_file": str(rel),
            "source_modified": iso_time(source.stat().st_mtime),
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    write_json(manifest_path, manifest)
    return manifest_path


def pull_staging_aux(path, task_names, examples_per_task, levels, max_tokens, aux_mode,
                     staging_repo, dedup=True):
    """Build LOCAL_AUX JSON by pulling a pre-built HF staging repo (rows keyed by 'task'),
    instead of generating locally. Fast path: data is produced on a cluster and pushed to HF."""
    from datasets import load_dataset
    path = Path(path)
    data = {name: [] for name in task_names}
    seen = {name: set() for name in task_names}
    remaining = set(task_names)
    print(f"pull staging: {staging_repo}  ({len(task_names)} tasks, dedup={dedup})", flush=True)
    for x in load_dataset(staging_repo, split="train", streaming=True):
        t = x.get("task") or ""
        if t not in remaining:
            continue
        ans = x.get("answer")
        if ans is None:
            continue
        p = x.get("prompt") or ""
        if dedup:
            if p in seen[t]:
                continue
            seen[t].add(p)
        data[t].append([p, str(ans)])
        if len(data[t]) >= examples_per_task:
            remaining.discard(t)
            if not remaining:
                break
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script_version": SCRIPT_VERSION,
        "source": "staging",
        "staging_repo": staging_repo,
        "dedup": dedup,
        "examples_per_task": examples_per_task,
        "levels": levels,
        "max_tokens": max_tokens,
        "aux_mode": aux_mode,
        "tasks": {},
    }
    for name in task_names:
        if not data[name]:
            print(f"  ! staging repo has no rows for {name}", file=sys.stderr)
        manifest["tasks"][name] = {
            "n": len(data[name]),
            "behavior_hash": get_task(name).behavior_hash(),
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    write_json(manifest_path, manifest)
    return manifest_path


def materialize_aux(aux_path, task_names, args):
    """Produce LOCAL_AUX from local generators (--source generate) or a staging HF repo (--source staging)."""
    if args.source == "staging":
        return pull_staging_aux(aux_path, task_names, args.aux_examples, args.aux_levels,
                                args.aux_max_tokens, args.aux_mode, args.staging_repo, args.dedup)
    return build_aux_data(aux_path, task_names, args.aux_examples, args.aux_levels,
                          args.aux_max_tokens, args.refresh, args.aux_mode, args.dedup)


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


def build_records(local, inventory, scores, contrastive_scores=None):
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
    registered = set(list_tasks())

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
            fmt(row.get("dolci_delta"), 4, signed=True),
            fmt(row.get("bbh_delta"), 3, signed=True),
            fmt(row.get("fw_delta"), 4, signed=True),
            _pair(row.get("prompt_tokens_mean"), row.get("answer_tokens_mean"), 0, "/"),
            _pair(row.get("acc_start"), row.get("acc_end"), 2, "→"),
            (row.get("behavior_hash", "") or "")[:7],
        ])

    lines.append("## Ranking")
    lines.append("")
    lines.append("Lower delta = helped. `score` higher = better helper. `tok` = prompt/answer tokens, "
                 "`acc` = start→end (both diagnostic). flan delta is in the JSON sidecar.")
    lines.append("")
    lines.append(markdown_table(rows, [
        "#", "task", "score", "dolci", "bbh", "fw", "tok", "acc", "hash",
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

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n")


def default_results_dirs():
    return [ROOT / "per_task_results"]


def clean_run_tag(tag):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(tag).strip().lstrip("_"))


def run_hash(task_names, args):
    inventory = task_inventory(task_names)
    payload = {
        "tasks": task_names,
        "hashes": {name: inventory.get(name, {}).get("behavior_hash", "") for name in task_names},
        "main_data": args.main_data,
        "seed": args.seed,
        "train_steps": args.train_steps,
        "mix_aux": args.mix_aux,
        "aux_examples": args.aux_examples,
        "aux_levels": args.aux_levels,
        "aux_max_tokens": args.aux_max_tokens,
        "aux_mode": args.aux_mode,
        "source": args.source,
        "dedup": args.dedup,
    }
    return hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:10]


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


def aux_manifest_fresh(aux_path, task_names, args):
    aux_path = Path(aux_path)
    manifest = load_json(aux_path.with_suffix(aux_path.suffix + ".manifest.json"))
    if not isinstance(manifest, dict):
        return False
    expected = {
        "script_version": SCRIPT_VERSION,
        "source": args.source,
        "dedup": args.dedup,
        "examples_per_task": args.aux_examples,
        "levels": args.aux_levels,
        "max_tokens": args.aux_max_tokens,
        "aux_mode": args.aux_mode,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            return False
    tasks = manifest.get("tasks", {})
    inventory = task_inventory(task_names)
    for name in task_names:
        rec = tasks.get(name)
        if not rec or rec.get("n", 0) <= 0:
            return False
        if rec.get("behavior_hash") != inventory.get(name, {}).get("behavior_hash"):
            return False
    return True


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

    args.run_tag = clean_run_tag(args.run_tag or f"LOCAL_{run_hash(task_names, args)}")
    if not args.build_aux:
        args.build_aux = str(ROOT / "task_influence_work" / f"{args.run_tag}_{args.aux_mode}.json")
    aux_path = Path(args.build_aux).expanduser()
    if not aux_path.is_absolute():
        aux_path = ROOT / aux_path

    if args.refresh or args.force_run or not aux_path.exists() or not aux_manifest_fresh(aux_path, task_names, args):
        manifest_path = materialize_aux(aux_path, task_names, args)
        print(f"wrote {aux_path}")
        print(f"wrote {manifest_path}")
    else:
        print(f"aux cache fresh: {aux_path}")

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
        "LOCAL_AUX": str(aux_path),
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
    parser.add_argument("--out", default="scripts/TASK_INFLUENCE.md")
    parser.add_argument("--cache", default=".task_influence_cache.json")
    parser.add_argument("--json-out", default=None,
                        help="Machine-readable JSON output. Default: --out with .json suffix.")
    parser.add_argument("--build-aux", default=None,
                        help=("Write LOCAL_AUX generator data JSON keyed by task. "
                              "Use an ignored path such as task_influence_work/aux.json."))
    parser.add_argument("--aux-examples", type=int, default=256,
                        help="Examples per task for --build-aux.")
    parser.add_argument("--aux-levels", nargs="+", type=int, default=[0, 1, 2],
                        help="Difficulty levels sampled for --build-aux.")
    parser.add_argument("--aux-max-tokens", type=int, default=5000,
                        help="Drop generated aux examples above this prompt+answer token budget.")
    parser.add_argument("--aux-mode", choices=("instruct", "contrastive"), default="instruct",
                        help="LOCAL_AUX format: original prompt/answer or verification yes/no.")
    parser.add_argument("--results-dir", action="append", default=None,
                        help="Directory with influence_*.json and sat_*.json. Can repeat.")
    parser.add_argument("--include", action="append", default=[],
                        help="Only use result files whose filename contains this string. Can repeat.")
    parser.add_argument("--contrastive-include", action="append", default=["CONTRAST"],
                        help="Filename substring(s) for contrastive influence files.")
    parser.add_argument("--exclude", action="append", default=[],
                        help="Skip result files whose filename contains this string. Can repeat.")
    parser.add_argument("--tasks", nargs="*", default=None)
    parser.add_argument("--samples", type=int, default=4,
                        help="Validation samples per task for local generator metrics.")
    parser.add_argument("--refresh", action="store_true",
                        help="Recompute local metrics even when task behavior hashes match.")
    parser.add_argument("--no-local", action="store_true",
                        help="Skip local task generation/validation and only aggregate result JSONs.")
    parser.add_argument("--weight", action="append", default=[],
                        help="Override target score weight, e.g. --weight flan=3 --weight fw=0.5")
    parser.add_argument("--profile", choices=sorted(WEIGHT_PROFILES), default="dolci",
                        help="Named scoring profile. --weight overrides individual values.")
    parser.add_argument("--run-influence", action="store_true",
                        help="Build/reuse aux data and launch the raw per-task influence trainer.")
    parser.add_argument("--runner", default=str(ROOT / "scripts" / "per_task_influence.py"),
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
    parser.add_argument("--source", choices=("generate", "staging"), default="generate",
                        help="Aux data source: 'generate' locally from task generators (default), or "
                             "'staging' to pull a pre-built HF repo (fast; built on a cluster).")
    parser.add_argument("--staging-repo", default="reasoning-core/staging",
                        help="HF dataset repo for --source staging (rows keyed by 'task').")
    parser.add_argument("--dedup", action=argparse.BooleanOptionalAction, default=True,
                        help="Drop duplicate prompts per task in the aux data (--no-dedup to keep them).")
    parser.add_argument("--aux-dataset", choices=("rc", "rgym"), default="rc")
    parser.add_argument("--main-data", choices=("dolci", "flan", "fw"), default="dolci")
    parser.add_argument("--model", default="HuggingFaceTB/SmolLM2-135M")
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
        run_info = launch_influence_run(args, task_names)
        run_dir = runner_results_dir(args)
        if run_dir not in results_dirs:
            results_dirs.insert(0, run_dir)
        if not args.include:
            args.include = [args.run_tag]
        if run_info.get("launched") and not args.foreground:
            print("raw influence run is in progress; rerun this command after it completes to refresh the report")
            return

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

    if args.build_aux and not args.run_influence:
        manifest_path = materialize_aux(Path(args.build_aux), task_names, args)
        print(f"wrote {args.build_aux}")
        print(f"wrote {manifest_path}")

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
    records = build_records(local, inventory, scores, c_scores)
    json_out = args.json_out or str(Path(args.out).with_suffix(".json"))
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
