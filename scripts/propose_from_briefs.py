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
# `propose` writes the archive and *then* exits 2 when a wave accepted fewer than --count.
# That is a wave that finished with a small yield, not a wave that failed: the archive
# exists and the resume rule skips this brief from now on, so counting it as a failure
# both misreports it and, three in a row, stops the job. Against a catalog of three
# hundred tasks a short wave is the normal outcome -- the first one accepted 1 of 36.
INCOMPLETE = 2


def briefs(with_shared=True):
    """(slug, prompt) per brief, each prompt carrying the shared instruction.

    Joined here rather than written into all forty-three texts, so the standing advice can
    be revised in one place while the briefs stay the ideas someone actually had. The
    shared line tells the proposer to reach past the standard repertoire, which is right
    for a catalog this mature and wrong for a wave that is meant to fill a known gap --
    sometimes a classic is exactly what is wanted -- so `with_shared=False` sends the
    briefs as written.
    """
    document = yaml.safe_load(BRIEFS.read_text())
    shared = " ".join((document.get("shared") or "").split()) if with_shared else ''
    return [(brief["slug"], _joined(" ".join(brief["text"].split()), shared))
            for group in document["groups"] for brief in group["briefs"]]


def _joined(text, shared):
    """The brief and the shared instruction as two sentences, not one run-on."""
    return f"{text.rstrip('.')}. {shared}" if shared else text


def accepted(name):
    """How many proposals the wave kept, for a log that shows novelty attrition."""
    try:
        document = yaml.safe_load((ARCHIVE / f"{name}.yaml").read_text()) or {}
    except OSError:
        return "?"
    return len(document.get("proposals") or [])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="k3", help="wave name prefix")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--pause-seconds", type=int, default=60)
    parser.add_argument("--log-dir", type=Path, default=ROOT / "runs" / "briefs")
    parser.add_argument(
        "--shared", action=argparse.BooleanOptionalAction, default=True,
        help="append briefs.yaml's shared instruction, which tells the proposer the"
             " catalog already has the classic algorithms; --no-shared sends the briefs"
             " as written, for a wave meant to fill a known gap with a classic")
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    arguments.log_dir.mkdir(parents=True, exist_ok=True)

    every = briefs(arguments.shared)
    pending = [(slug, text) for slug, text in every
               if not (ARCHIVE / f"{arguments.prefix}_{slug}.yaml").exists()]
    done = len(every) - len(pending)
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
        if completed.returncode in (0, INCOMPLETE):
            failures = 0
            print(f"    ok in {minutes:.0f}m, {accepted(name)} accepted", flush=True)
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
