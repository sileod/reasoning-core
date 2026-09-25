#!/usr/bin/env python3
"""Keep datasets/<name>/README.md (the HF dataset card's source of truth) honest.

The card is hand-written. This script only touches what is derivable from the data:

  - YAML `dataset_info` (features, split sizes) and `size_categories`
  - inline numbers wrapped in <!-- stat:KEY -->...<!-- /stat -->
  - the "· N" count of each `- **Area** · N: `task`, ...` catalogue line

Which area a task belongs to stays a human decision: a task present in the data but
absent from the catalogue (or the reverse) is an error to fix by hand, not auto-filled.

  python scripts/dataset_card.py stats              # scan the Hub -> stats.json
  python scripts/dataset_card.py render [--check]   # stats.json -> README.md
  python scripts/dataset_card.py push               # README.md -> Hub
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1] / "datasets"
ORG = "reasoning-core"
STAT = re.compile(r"(<!-- stat:(\w+) -->)(.*?)(<!-- /stat -->)")
ROW = re.compile(r"^(- \*\*(?P<area>[^*]+)\*\* · )(?P<n>\d+)(: )(?P<tasks>.*?)()$", re.M)
TASK = re.compile(r"`([^`]+)`")
SIZE_BUCKETS = [(1e3, "n<1K"), (1e4, "1K<n<10K"), (1e5, "10K<n<100K"), (1e6, "100K<n<1M"),
                (1e7, "1M<n<10M"), (1e8, "10M<n<100M"), (1e9, "100M<n<1B"), (float("inf"), "n>1B")]


def paths(name):
    return ROOT / name / "README.md", ROOT / name / "stats.json"


def scan(name, revision):
    """Read only the `task` and `mode` columns of every shard; exact, and cheap next to the full rows."""
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem

    repo = f"{ORG}/{name}"
    sha = HfApi().dataset_info(repo, revision=revision).sha
    files = sorted(f for f in HfApi().list_repo_files(repo, repo_type="dataset", revision=sha)
                   if f.endswith(".parquet"))
    fs = HfFileSystem()
    splits, tasks, modes, schema = Counter(), Counter(), Counter(), None
    for i, f in enumerate(files, 1):
        with fs.open(f"datasets/{repo}@{sha}/{f}") as fh:
            pf = pq.ParquetFile(fh)
            schema = schema or pf.schema_arrow
            table = pf.read(columns=["task", "mode"])
        splits[Path(f).name.split("-")[0]] += table.num_rows
        for d in pc.value_counts(table["task"]).to_pylist():
            tasks[d["values"]] += d["counts"]
        for d in pc.value_counts(table["mode"]).to_pylist():
            modes[d["values"]] += d["counts"]
        print(f"[{i}/{len(files)}] {f}", file=sys.stderr)
    return {
        "repo": repo,
        "revision": sha,
        "features": [{"name": n, "dtype": str(t)} for n, t in zip(schema.names, schema.types)],
        "splits": dict(sorted(splits.items())),
        "tasks": dict(sorted(tasks.items())),
        "modes": dict(modes.most_common()),
    }


def render(text, stats):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit("README.md has no YAML front matter")
    meta = yaml.safe_load(m.group(1))
    total = sum(stats["splits"].values())
    meta["dataset_info"] = {
        "features": stats["features"],
        "splits": [{"name": s, "num_examples": n} for s, n in stats["splits"].items()],
    }
    meta["size_categories"] = [next(label for bound, label in SIZE_BUCKETS if total < bound)]
    body = text[m.end():]

    modes = [f"`{m}`" for m in stats["modes"]]
    values = {
        "n_tasks": len(stats["tasks"]),
        "n_rows": f"{total:,}",
        "modes": modes[0] if len(modes) == 1 else ", ".join(modes[:-1]) + f", or {modes[-1]}",
    }
    unknown = {k for _, k, _, _ in STAT.findall(body)} - values.keys()
    if unknown:
        raise SystemExit(f"unknown stat markers: {sorted(unknown)}")
    body = STAT.sub(lambda s: f"{s[1]}{values[s[2]]}{s[4]}", body)

    listed = Counter(t for row in ROW.finditer(body) for t in TASK.findall(row["tasks"]))
    problems = []
    if not listed:
        problems.append("no `- **Area** · N: ...` catalogue lines found")
    if dup := sorted(t for t, c in listed.items() if c > 1):
        problems.append(f"listed more than once: {dup}")
    if missing := sorted(set(stats["tasks"]) - set(listed)):
        problems.append(f"in the data but not in the catalogue (assign an area): {missing}")
    if stale := sorted(set(listed) - set(stats["tasks"])):
        problems.append(f"in the catalogue but not in the data (remove): {stale}")
    if problems:
        raise SystemExit("task catalogue out of sync:\n  " + "\n  ".join(problems))
    body = ROW.sub(lambda r: f"{r[1]}{len(TASK.findall(r['tasks']))}{r[4]}{r['tasks']}{r[6]}", body)

    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000)
    return f"---\n{front}---\n{body}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["stats", "render", "push"])
    ap.add_argument("--name", default="procedural-pile")
    ap.add_argument("--revision", default="main", help="stats: Hub revision to scan")
    ap.add_argument("--check", action="store_true", help="render: fail instead of writing")
    args = ap.parse_args()
    readme, stats_path = paths(args.name)

    if args.command == "stats":
        stats = scan(args.name, args.revision)
        stats_path.write_text(json.dumps(stats, indent=1) + "\n")
        print(f"{stats_path}: {len(stats['tasks'])} tasks, {stats['splits']} @ {stats['revision'][:12]}")
    elif args.command == "render":
        old = readme.read_text()
        new = render(old, json.loads(stats_path.read_text()))
        if new == old:
            print(f"{readme}: up to date")
        elif args.check:
            raise SystemExit(f"{readme}: stale; run `python scripts/dataset_card.py render`")
        else:
            readme.write_text(new)
            print(f"{readme}: updated")
    else:
        from huggingface_hub import HfApi
        new = render(readme.read_text(), json.loads(stats_path.read_text()))
        if new != readme.read_text():
            raise SystemExit(f"{readme}: stale; render and commit it before pushing")
        info = HfApi().upload_file(path_or_fileobj=str(readme), path_in_repo="README.md",
                                   repo_id=f"{ORG}/{args.name}", repo_type="dataset",
                                   commit_message="dataset card: sync from GitHub datasets/")
        print(info)


if __name__ == "__main__":
    main()
