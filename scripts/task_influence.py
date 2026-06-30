#!/usr/bin/env python
"""Analyze RC task influence signals from local generation and SFT result JSONs.

The script is intentionally read-only with respect to tasks. It caches local
task smoke metrics by task behavior hash, then rewrites a compact Markdown
report every run.
"""

import argparse
import csv
import hashlib
import inspect
import json
import math
import re
import statistics as stats
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
GITHUB_TASKS_BASE = "https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks"
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


def markdown_fence(text):
    text = str(text)
    ticks = "```"
    if ticks in text:
        ticks = "````"
    return f"{ticks}\n{text}\n{ticks}"


def write_gallery(path, task_names, refresh, samples):
    """Write a compact gallery, rebuilding examples only when validation cache misses."""
    def clean_section(text):
        lines = text.rstrip().splitlines()
        while lines and not lines[-1].strip():
            lines.pop()
        if lines and lines[-1].strip() == "---":
            lines.pop()
        return "\n".join(lines).rstrip() + "\n"

    path = Path(path)
    existing_sections = {}
    if path.exists() and not refresh:
        current_name = None
        current_lines = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                if current_name and current_lines:
                    existing_sections[current_name] = clean_section("\n".join(current_lines))
                current_lines = [line]
                title = line[3:].strip()
                title = re.sub(r"^\[([^\]]+)\].*$", r"\1", title)
                current_name = title
            elif current_name:
                current_lines.append(line)
        if current_name and current_lines:
            existing_sections[current_name] = clean_section("\n".join(current_lines))

    lines = ["# Task Gallery", ""]
    failures = []
    reused = 0
    generated = 0
    for name in task_names:
        try:
            task = get_task(name)
            old = existing_sections.get(name)
            if old and f"- hash: `{task.behavior_hash()}`" in old:
                lines.append(old.rstrip())
                lines.extend(["", "---", ""])
                reused += 1
                continue

            examples = task.validate(n_samples=max(1, samples), cache=True, refresh=refresh)
            generated += 1
            example = sorted(examples, key=lambda ex: len(ex.prompt) - len(str(ex.answer)))[0]
            source = Path(inspect.getfile(task.__class__)).resolve()
            rel = source.relative_to(ROOT) if source.is_relative_to(ROOT) else source
            github_rel = str(rel).split("reasoning_core/tasks/")[-1]
            link = f"{GITHUB_TASKS_BASE}/{github_rel}" if "reasoning_core/tasks/" in str(rel) else str(rel)
            lines.extend([
                f"## [{name}]({link})",
                "",
                f"- hash: `{task.behavior_hash()}`",
                f"- modified: {iso_time(source.stat().st_mtime)}",
                "",
                "**Prompt:**",
                markdown_fence(example.prompt),
                "",
                "**Answer:**",
                markdown_fence(example.answer),
                "",
                "",
            ])
        except Exception as exc:
            failures.append((name, repr(exc)))
            lines.extend([f"## {name}", "", f"Failed: `{repr(exc)}`", ""])
        lines.extend(["---", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    return {"failures": failures, "reused": reused, "generated": generated}


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


def build_aux_data(path, task_names, examples_per_task, levels, max_tokens, refresh, aux_mode):
    """Build LOCAL_AUX JSON keyed as task -> [[prompt, completion], ...]."""
    path = Path(path)
    data = {}
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script_version": SCRIPT_VERSION,
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
        examples_all = []
        per_level = max(1, math.ceil(examples_per_task / max(1, len(levels))))
        for level in levels:
            if refresh:
                examples = task.generate_balanced_batch(
                    batch_size=per_level,
                    max_tokens=max_tokens,
                    level=level,
                )
            else:
                task.config.set_level(level)
                examples = task.validate(n_samples=per_level, cache=True)
            for ex in examples:
                if len(examples_all) >= examples_per_task * (2 if aux_mode == "contrastive" else 1):
                    break
                if max_tokens:
                    pt = ex.metadata.get("_prompt_tokens", 0) or 0
                    at = ex.metadata.get("_answer_tokens", 0) or 0
                    if pt + at > max_tokens:
                        continue
                examples_all.append(ex)
            if len(examples_all) >= examples_per_task * (2 if aux_mode == "contrastive" else 1):
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


def write_machine_outputs(json_path, csv_path, records, influence_runs, sat_runs, contrast_runs, args):
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

    if not csv_path:
        return

    fieldnames = [
        "rank", "task", "category", "influence_score", "n_runs",
        "contrastive_score",
        "flan_delta", "fw_delta", "bbh_delta", "dolci_delta",
        "acc_start", "acc_end", "prompt_tokens_mean", "answer_tokens_mean",
        "behavior_hash", "source_file", "source_modified", "ok", "issue",
    ]
    with Path(csv_path).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            row = {k: rec.get(k, "") for k in fieldnames}
            writer.writerow(row)


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
    targets = sorted({t for r in records for t in r.get("targets", {})})

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

    rows = []
    for row in records:
        rows.append([
            str(row["rank"]),
            row["task"],
            fmt(row["influence_score"], 3, signed=True),
            fmt(row.get("contrastive_score"), 3, signed=True),
            fmt(row.get("flan_delta"), 4, signed=True),
            fmt(row.get("bbh_delta"), 4, signed=True),
            fmt(row.get("fw_delta"), 4, signed=True),
            fmt(row.get("acc_start"), 3),
            fmt(row.get("acc_end"), 3),
            fmt(row.get("prompt_tokens_mean"), 1),
            fmt(row.get("answer_tokens_mean"), 1),
            row.get("source_modified", ""),
            row.get("behavior_hash", "") or "",
            "" if row.get("ok") or row.get("ok") is None else str(row.get("issue", ""))[:80],
        ])

    lines.append("## Ranking")
    lines.append("")
    lines.append(markdown_table(rows, [
        "#", "task", "influence_score", "contrastive_score", "flan_delta", "bbh_delta", "fw_delta",
        "acc_start", "acc_end", "prompt_tok", "answer_tok", "modified", "hash", "issue",
    ]))
    lines.append("")

    if targets:
        lines.append("## Target Deltas")
        lines.append("")
        detail_rows = []
        for row in records:
            detail_rows.append([
                row["task"],
                *[
                    fmt(row["targets"].get(t, {}).get("mean"), 4, signed=True)
                    for t in targets
                ],
            ])
        lines.append(markdown_table(detail_rows, ["task", *[f"{t}_delta" for t in targets]]))
        lines.append("")

    lines.append("## Inputs")
    lines.append("")
    lines.append("Influence runs:")
    for run in influence_runs[:80]:
        lines.append(f"- `{Path(run['file']).name}`")
    if len(influence_runs) > 80:
        lines.append(f"- ... {len(influence_runs) - 80} more")
    lines.append("")
    lines.append("Saturation runs:")
    for run in sat_runs[:80]:
        lines.append(f"- `{Path(run['file']).name}`")
    if len(sat_runs) > 80:
        lines.append(f"- ... {len(sat_runs) - 80} more")
    lines.append("")
    if contrast_runs:
        lines.append("Contrastive influence runs:")
        for run in contrast_runs[:80]:
            lines.append(f"- `{Path(run['file']).name}`")
        lines.append("")

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n")


def default_results_dirs():
    candidates = [
        ROOT / "per_task_results",
        Path("~/sandboxes/rc_grad/per_task_results").expanduser(),
    ]
    return [p for p in candidates if p.exists()] or [ROOT / "per_task_results"]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="scripts/TASK_INFLUENCE.md")
    parser.add_argument("--cache", default=".task_influence_cache.json")
    parser.add_argument("--json-out", default=None,
                        help="Machine-readable JSON output. Default: --out with .json suffix.")
    parser.add_argument("--csv-out", default=None,
                        help="Optional CSV output. By default only Markdown and JSON are written.")
    parser.add_argument("--gallery-out", default=None,
                        help="Optionally rebuild a human-readable task gallery.")
    parser.add_argument("--gallery-refresh", action="store_true",
                        help="Refresh all gallery cached examples instead of only changed hashes.")
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
    return parser.parse_args()


def main():
    args = parse_args()
    args.weights = parse_weights(args.profile, args.weight)
    task_names = args.tasks or list_tasks()
    results_dirs = [Path(p).expanduser() for p in (args.results_dir or default_results_dirs())]

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

    if args.gallery_out:
        gallery = write_gallery(args.gallery_out, task_names, args.gallery_refresh or args.refresh, args.samples)
        print(
            f"wrote {args.gallery_out} "
            f"(generated={gallery['generated']} reused={gallery['reused']})"
        )
        if gallery["failures"]:
            print(f"gallery failures: {len(gallery['failures'])}", file=sys.stderr)

    if args.build_aux:
        manifest_path = build_aux_data(
            args.build_aux,
            task_names,
            args.aux_examples,
            args.aux_levels,
            args.aux_max_tokens,
            args.refresh,
            args.aux_mode,
        )
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

    all_names = sorted(set(task_names) | set(influence) | set(saturation))
    inventory = task_inventory(all_names)
    scores = aggregate_scores(all_names, influence, saturation, args.weights)
    c_scores = contrastive_scores(all_names, contrastive)
    records = build_records(local, inventory, scores, c_scores)
    json_out = args.json_out or str(Path(args.out).with_suffix(".json"))
    csv_out = args.csv_out
    write_markdown(args.out, records, influence_runs, sat_runs, contrast_runs, args)
    write_machine_outputs(json_out, csv_out, records, influence_runs, sat_runs, contrast_runs, args)

    print(f"wrote {args.out}")
    print(f"wrote {json_out}")
    if csv_out:
        print(f"wrote {csv_out}")
    for row in records[:12]:
        print(
            f"{row['task']:<32} influence={fmt(row['influence_score'], 3, True):>8} "
            f"flan={fmt(row.get('flan_delta'), 4, True):>9} "
            f"fw={fmt(row.get('fw_delta'), 4, True):>9} "
            f"acc={fmt(row.get('acc_start'), 3):>5}->{fmt(row.get('acc_end'), 3):<5}"
        )


if __name__ == "__main__":
    main()
