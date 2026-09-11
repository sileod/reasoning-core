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
import re
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
    parser.add_argument(
        "--model", default="",
        help="comma-separated models in preference order, passed to `propose`; empty"
             " leaves the CLI default")
    parser.add_argument(
        "--api-key-env", default="",
        help="comma-separated credential variables to share round-robin, so one key's"
             " quota does not cap the run")
    parser.add_argument(
        "--passes", type=int, default=3,
        help="sweep the unarchived briefs this many times; a wave that fails writes no"
             " archive, so a later pass retries it")
    parser.add_argument(
        "--cooldowns", type=int, default=8,
        help="how many times to wait out a provider that is refusing everything before"
             " counting the wave as failed")
    parser.add_argument(
        "--cooldown-seconds", type=int, default=1800,
        help="how long each of those waits is")
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()
    arguments.log_dir.mkdir(parents=True, exist_ok=True)

    every = briefs(arguments.shared)
    for sweep in range(1, arguments.passes + 1):
        pending = [(slug, text) for slug, text in every
                   if not (ARCHIVE / f"{arguments.prefix}_{slug}.yaml").exists()]
        done = len(every) - len(pending)
        if not pending:
            print("every brief has a wave", flush=True)
            return 0
        print(f"pass {sweep}/{arguments.passes}: {len(pending)} briefs to run,"
              f" {done} already archived", flush=True)
        status = sweep_once(arguments, pending)
        if status is not None:
            return status
    print("passes exhausted; re-run to keep retrying what is left", flush=True)
    return 0


# NIM answers a quota block with a bare `{"status":429,"title":"Too Many Requests"}` and
# no Retry-After, so there is nothing to read but the status itself. It refuses a two-token
# request just as fast as a wave, which is what separates it from ordinary throttling: no
# amount of per-call backoff gets through, and moving to the next brief only spends the
# same refusal on a different prompt.
RATE_LIMITED = re.compile(r"\b429\b|Too Many Requests")


def rate_limited(log_path):
    """Did this wave die because the provider is refusing everything right now?"""
    try:
        tail = log_path.read_text()[-4000:]
    except OSError:
        return False
    return bool(RATE_LIMITED.search(tail))


def run_wave(arguments, command, log_path):
    """Run one wave, waiting out a provider that is refusing everything.

    A quota block is not a failed wave, it is a closed door, and the brief behind it is
    still owed. Waiting costs nothing but time -- which an overnight job has -- while
    giving up costs the night: the block that prompted this arrived at 01:32 and would
    have burned the give-up budget on three waves that could not have succeeded.
    """
    for cooldown in range(arguments.cooldowns + 1):
        started = time.time()
        with log_path.open("w") as log:
            completed = subprocess.run(command, cwd=ROOT, stdout=log,
                                       stderr=subprocess.STDOUT)
        minutes = (time.time() - started) / 60
        if completed.returncode in (0, INCOMPLETE) or not rate_limited(log_path):
            return completed, minutes
        if cooldown == arguments.cooldowns:
            print(f"    still rate limited after {arguments.cooldowns} waits",
                  flush=True)
            return completed, minutes
        print(f"    rate limited after {minutes:.0f}m; waiting"
              f" {arguments.cooldown_seconds // 60}m"
              f" ({cooldown + 1}/{arguments.cooldowns})", flush=True)
        time.sleep(arguments.cooldown_seconds)
    raise AssertionError("unreachable")


def sweep_once(arguments, pending):
    """One pass over the briefs with no archive. A status means stop, None means continue.

    A brief that fails writes no archive, so the next pass finds it again -- which is the
    whole reason passes exist. Two of the first three waves after a restart died on a
    truncated stream and on a 429 that outlasted sixteen minutes of backoff; both are the
    kind of failure that simply works later, and a single-pass driver dropped them until
    somebody noticed and restarted it.
    """
    failures = 0
    for index, (slug, text) in enumerate(pending, start=1):
        name = f"{arguments.prefix}_{slug}"
        command = [sys.executable, "-m", "reasoning_core.task_search", "propose", name,
                   "--brief", text, "--count", str(arguments.count),
                   "--rounds", str(arguments.rounds)]
        # Passed through only when set, so an unconfigured run renders the command it
        # always did and the CLI keeps owning the defaults.
        if arguments.model:
            command += ["--model", arguments.model]
        if arguments.api_key_env:
            command += ["--api-key-env", arguments.api_key_env]
        if arguments.dry_run:
            print(f"[{index}/{len(pending)}] would run: {name}", flush=True)
            continue
        print(f"[{index}/{len(pending)}] {time.strftime('%H:%M')} {name}", flush=True)
        log_path = arguments.log_dir / f"{slug}.log"
        completed, minutes = run_wave(arguments, command, log_path)
        if completed.returncode in (0, INCOMPLETE):
            failures = 0
            print(f"    ok in {minutes:.0f}m, {accepted(name)} accepted", flush=True)
        else:
            failures += 1
            print(f"    FAILED (exit {completed.returncode}) after {minutes:.0f}m"
                  f" -- see {log_path}", flush=True)
            if failures >= GIVE_UP_AFTER:
                print(f"stopping: {failures} waves failed in a row", flush=True)
                return 1
        time.sleep(arguments.pause_seconds)
    return None


if __name__ == "__main__":
    raise SystemExit(main())
