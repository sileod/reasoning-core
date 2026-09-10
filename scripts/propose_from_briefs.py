#!/usr/bin/env python3
"""Run one proposal wave per brief, slowly, until every brief has an archive.

Waves run one at a time because the proposer and the critic share rate limits with each
other and with anything else pointed at the same providers, and because a wave that is
merely slow is fine: kimi-k3 behind NIM takes tens of minutes, and forty-three of them is
about a day.

Resume is the archive itself. `propose` refuses to overwrite one, so a brief that already
has a wave is skipped and a run interrupted at any point continues where it stopped.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

import yaml

ROOT = Path(__file__).resolve().parents[1]
BRIEFS = ROOT / "reasoning_core" / "task_search" / "proposals" / "briefs.yaml"
ARCHIVE = ROOT / "reasoning_core" / "task_search" / "proposals" / "archive"
# Consecutive failures that mean the provider is gone rather than one wave being unlucky.
# Without this the job spends the night failing forty-three times in a row.
GIVE_UP_AFTER = 3


def briefs():
    document = yaml.safe_load(BRIEFS.read_text())
    return [(brief["slug"], " ".join(brief["text"].split()))
            for group in document["groups"] for brief in group["briefs"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="k3", help="wave name prefix")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--pause-seconds", type=int, default=60)
    parser.add_argument("--log-dir", type=Path, default=ROOT / "runs" / "briefs")
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    arguments.log_dir.mkdir(parents=True, exist_ok=True)

    pending = [(slug, text) for slug, text in briefs()
               if not (ARCHIVE / f"{arguments.prefix}_{slug}.yaml").exists()]
    done = len(briefs()) - len(pending)
    print(f"{len(pending)} briefs to run, {done} already archived", flush=True)

    failures = 0
    for index, (slug, text) in enumerate(pending, start=1):
        name = f"{arguments.prefix}_{slug}"
        command = [sys.executable, "-m", "reasoning_core.task_search", "propose", name,
                   "--brief", text, "--count", str(arguments.count),
                   "--rounds", str(arguments.rounds)]
        if arguments.dry_run:
            print(f"[{index}/{len(pending)}] would run: {name}", flush=True)
            continue
        started = time.time()
        print(f"[{index}/{len(pending)}] {time.strftime('%H:%M')} {name}", flush=True)
        with (arguments.log_dir / f"{slug}.log").open("w") as log:
            completed = subprocess.run(command, cwd=ROOT, stdout=log,
                                       stderr=subprocess.STDOUT)
        minutes = (time.time() - started) / 60
        if completed.returncode == 0:
            failures = 0
            print(f"    ok in {minutes:.0f}m", flush=True)
        else:
            failures += 1
            print(f"    FAILED (exit {completed.returncode}) after {minutes:.0f}m"
                  f" -- see {arguments.log_dir / f'{slug}.log'}", flush=True)
            if failures >= GIVE_UP_AFTER:
                print(f"stopping: {failures} waves failed in a row", flush=True)
                return 1
        time.sleep(arguments.pause_seconds)
    print("every brief has a wave", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
