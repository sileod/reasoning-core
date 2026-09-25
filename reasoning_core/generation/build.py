"""Build one dataset version into a run directory, then upload it to a Hub staging repo.

    python -m reasoning_core.generation init     --run-dir R --version rc13 [--roster FILE]
    python -m reasoning_core.generation generate --run-dir R [--workers N]
    python -m reasoning_core.generation collect  --run-dir R [--loop]
    python -m reasoning_core.generation submit   --run-dir R --version rc13 [--nodes 16] [--smoke]

A run directory holds everything a build reads or writes:

    run.json                    frozen configuration; every other command reads it
    generated_data/<version>/   <task>-<idx>.jsonl, one per batch (.lock while claimed,
                                .fail counting failed attempts)
    upload_state/               collector progress
    logs/                       <host>.errors.log, <host>.batches.jsonl, scheduler output

`generate` can run on any number of machines sharing the directory: workers claim batches
with exclusive lock files and skip finished ones, so a killed or resubmitted node resumes.
`submit` is the only code that knows about OAR (Grid'5000).
"""
import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_var, "1")  # before numpy; one BLAS thread per worker process

import ast
import ctypes
import fcntl
import json
import math
import multiprocessing as mp
import random
import resource
import shlex
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO / "reasoning_core"

DEFAULTS = {
    "levels": [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 6],
    "rows_per_task": 20_000,
    "batch_size": 16,
    "max_tokens": 5_000,
    "dataset": "staging",
}
# Highest level a task is generated at, when lower than the run's levels allow.
LEVEL_CAPS = {
    "proof_reconstruction": 2,
    "bayesian_association": 0,
    "bayesian_intervention": 0,
    "logic_nli": 3,
    "evidence_retrieval": 3,
    "table_conversion": 4,
}
MAX_ATTEMPTS = 3            # failed attempts before a batch is given up on
LOCK_MARGIN_S = 600         # a lock older than batch_timeout + this was left by a dead node
EXIT_RECYCLE = 10           # worker reached its lifetime; the supervisor starts a fresh one
MAX_CRASHES = 5             # abnormal exits per worker slot before it is retired


# ---------------------------------------------------------------------------------------- run

def manifest_path(run_dir):
    return Path(run_dir) / "run.json"


def load_manifest(run_dir):
    path = manifest_path(run_dir)
    if not path.exists():
        raise SystemExit(f"{path} missing; run `init` first")
    return json.loads(path.read_text())


def data_dir(run_dir, manifest):
    return Path(run_dir) / "generated_data" / manifest["version"]


def read_roster(path):
    names = [line.split("#")[0].strip() for line in Path(path).read_text().splitlines()]
    return [n for n in names if n]


def resolve_tasks(names):
    from reasoning_core import get_task
    problems = []
    for name in names:
        try:
            get_task(name)
        except Exception as e:
            problems.append(f"{name}: {type(e).__name__}: {e}")
    if problems:
        raise SystemExit("roster does not resolve:\n  " + "\n  ".join(problems))
    return names


def git_revision():
    try:
        return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return None  # deployed copies (the G5K storage) carry no .git


def init(run_dir, version, roster=None, git_rev=None, **settings):
    """Write run.json once. Re-running with the same settings is a no-op, so resubmits resume;
    different settings for an existing run are refused rather than silently mixed."""
    settings = {k: v for k, v in settings.items() if v is not None}
    path = manifest_path(run_dir)
    if path.exists():
        manifest = json.loads(path.read_text())
        requested = dict(settings, version=version)
        if roster:
            requested["tasks"] = read_roster(roster)
        clash = {k: (manifest.get(k), v) for k, v in requested.items() if manifest.get(k) != v}
        if clash:
            raise SystemExit(f"{path} exists with different settings {clash}; "
                             "use a new version or run directory")
        rev = git_rev or git_revision()
        if rev and rev != manifest.get("git") and rev not in manifest.get("resumed_at", []):
            # Resuming with newer code is allowed (hotfixes), but the run must say so: rows
            # written after this point come from `rev`, not from the revision it started at.
            print(f"warning: {path} started at {manifest.get('git')}, resuming at {rev}", flush=True)
            manifest.setdefault("resumed_at", []).append(rev)
            _write_manifest(path, manifest)
        return manifest
    from reasoning_core import list_tasks
    manifest = {
        "version": version,
        **DEFAULTS,
        **settings,
        "tasks": resolve_tasks(read_roster(roster) if roster else list_tasks()),
        "git": git_rev or git_revision(),
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    for sub in ("logs", "upload_state"):
        (Path(run_dir) / sub).mkdir(parents=True, exist_ok=True)
    data_dir(run_dir, manifest).mkdir(parents=True, exist_ok=True)
    _write_manifest(path, manifest)
    return manifest


def _write_manifest(path, manifest):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=1) + "\n")
    os.replace(tmp, path)


def batch_jobs(manifest):
    per_task = math.ceil(manifest["rows_per_task"] / manifest["batch_size"])
    return [(task, i) for task in manifest["tasks"] for i in range(per_task)]


def progress(run_dir, manifest):
    """(finished batches, gave-up batches, total batches)."""
    done = failed = 0
    for entry in os.scandir(data_dir(run_dir, manifest)):
        if entry.name.endswith(".jsonl"):
            done += 1
        elif entry.name.endswith(".fail") and entry.stat().st_size >= MAX_ATTEMPTS:
            failed += 1
    return done, failed, len(batch_jobs(manifest))


# ----------------------------------------------------------------------------------- generate

def _claim(out, task, idx, stale_after):
    """Lock a batch nobody finished, gave up on, or holds; None when it is not ours to run."""
    stem = out / f"{task}-{idx}"
    final, lock, fail = (stem.with_suffix(s) for s in (".jsonl", ".lock", ".fail"))
    if final.exists():
        return None
    try:
        if fail.exists() and fail.stat().st_size >= MAX_ATTEMPTS:
            return None
        if lock.exists():
            if time.time() - lock.stat().st_mtime <= stale_after:
                return None
            lock.unlink()
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except OSError:
        return None  # another process won the race, or the file vanished under us
    return lock


def _kill_children(pid):
    """Kill every descendant of `pid`. Generators start helpers in their own session (the Lean
    REPL), so they outlive a killed or exiting worker unless reaped here."""
    try:
        children = psutil.Process(pid).children(recursive=True)
    except psutil.NoSuchProcess:
        return
    for child in children:
        try:
            child.kill()
        except psutil.NoSuchProcess:
            pass
    psutil.wait_procs(children, timeout=5)


def _limit_malloc_arenas(n=4):
    """glibc reserves up to 8 malloc arenas per core, 64 MB of address space each. On a 512-core
    node that alone exceeds the RLIMIT_AS cap and threads fail to start ("cannot allocate memory
    for thread-local data"). Cap them here and in the helpers a generator starts."""
    os.environ["MALLOC_ARENA_MAX"] = str(n)
    try:
        ctypes.CDLL("libc.so.6").mallopt(-8, n)  # M_ARENA_MAX
    except OSError:
        pass  # not glibc


def _work(run_dir, manifest, current, started, lifetime, mem_gb, stale_after):
    """One worker process: claim and run batches until none is left or the lifetime is spent."""
    try:
        _work_loop(run_dir, manifest, current, started, lifetime, mem_gb, stale_after)
    finally:
        _kill_children(os.getpid())


def _work_loop(run_dir, manifest, current, started, lifetime, mem_gb, stale_after):
    from reasoning_core.generation.worker import run_task
    _limit_malloc_arenas()
    if mem_gb:
        limit = int(mem_gb * 1024 ** 3)
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    random.seed(os.getpid() ^ time.time_ns())
    out = data_dir(run_dir, manifest)
    host = socket.gethostname().split(".")[0]
    logs = Path(run_dir) / "logs"
    errors, batches = logs / f"{host}.errors.log", logs / f"{host}.batches.jsonl"
    jobs = batch_jobs(manifest)
    order = list(range(len(jobs)))  # shuffle the visiting order, not the list: the supervisor
    random.shuffle(order)           # reads `current` as an index into batch_jobs(manifest)
    deadline = time.time() + lifetime
    while True:
        claimed = False
        for job_i in order:
            task, idx = jobs[job_i]
            lock = _claim(out, task, idx, stale_after)
            if lock is None:
                continue
            claimed = True
            cap = LEVEL_CAPS.get(task, max(manifest["levels"]))
            level = random.choice([l for l in manifest["levels"] if l <= cap] or [min(manifest["levels"])])
            current.value, started.value = job_i, time.time()
            try:
                ok, msg = run_task(task, idx, level, out, manifest["batch_size"],
                                   manifest["max_tokens"], log_path=batches)
            except Exception as e:  # run_task catches generation errors; this is anything else
                ok, msg = False, f"CRASH: {type(e).__name__}: {e}"
            if not ok:
                with open(out / f"{task}-{idx}.fail", "a") as f:
                    f.write("x")
                with open(errors, "a") as f:
                    f.write(f"{datetime.now():%F %T} {task}-{idx} L{level}: {msg}\n")
            lock.unlink(missing_ok=True)
            current.value = -1
            if time.time() > deadline:
                sys.exit(EXIT_RECYCLE)
        if not claimed:
            return  # nothing claimable: done here


def _release(out, task, idx, failed):
    if failed:
        with open(out / f"{task}-{idx}.fail", "a") as f:
            f.write("x")
    (out / f"{task}-{idx}.lock").unlink(missing_ok=True)


def generate(run_dir, workers=None, lifetime=900, batch_timeout=1200, mem_gb=50, report_every=60):
    """Supervise worker processes on this machine until no batch is left to claim.

    Workers are recycled after `lifetime` seconds (generators can leak), a batch running past
    `batch_timeout` gets its worker killed, and each worker is capped at `mem_gb` of address
    space. A killed or crashed worker's batch counts as a failed attempt and is released at
    once; a lock older than `batch_timeout` + LOCK_MARGIN_S was left by a dead node and is
    reclaimed by any worker. Returns progress() at exit."""
    manifest = load_manifest(run_dir)
    workers = workers or max(1, math.ceil((os.cpu_count() or 1) * 0.4))
    jobs = batch_jobs(manifest)
    out = data_dir(run_dir, manifest)
    ctx = mp.get_context("fork")
    slots = [{"proc": None, "finished": False, "crashes": 0, "current": ctx.Value("i", -1),
              "started": ctx.Value("d", 0.0)} for _ in range(workers)]
    print(f"generate {manifest['version']}: {len(manifest['tasks'])} tasks, {len(jobs)} batches, "
          f"{workers} workers on {socket.gethostname()}", flush=True)
    last_report = 0.0
    while True:
        now = time.time()
        for slot in slots:
            proc = slot["proc"]
            if slot["finished"]:
                continue
            if proc is not None and proc.is_alive():
                job_i = slot["current"].value
                if job_i >= 0 and now - slot["started"].value > batch_timeout:
                    _kill_children(proc.pid)
                    proc.kill()
                    proc.join()
                    task, idx = jobs[job_i]
                    _release(out, task, idx, failed=True)
                    print(f"killed {task}-{idx}: over {batch_timeout}s", flush=True)
                    slot["proc"] = None
                continue
            if proc is not None and proc.exitcode == 0:
                slot["finished"] = True
            elif proc is not None and proc.exitcode != EXIT_RECYCLE:
                # A worker that keeps dying outside run_task (import error, OOM kill) would
                # otherwise be restarted forever.
                slot["crashes"] += 1
                print(f"worker exited with {proc.exitcode} ({slot['crashes']}/{MAX_CRASHES})", flush=True)
                if slot["current"].value >= 0:  # it died mid-batch: count the attempt, free the batch
                    _release(out, *jobs[slot["current"].value], failed=True)
                slot["finished"] = slot["crashes"] >= MAX_CRASHES
            if not slot["finished"]:
                slot["current"].value = -1
                slot["proc"] = ctx.Process(target=_work, args=(
                    run_dir, manifest, slot["current"], slot["started"], lifetime, mem_gb,
                    batch_timeout + LOCK_MARGIN_S))
                slot["proc"].start()
        if all(s["finished"] for s in slots):
            break
        if now - last_report >= report_every:
            done, failed, total = progress(run_dir, manifest)
            print(f"{datetime.now():%F %T} {done}/{total} batches, {failed} given up", flush=True)
            last_report = now
        time.sleep(0.5)
    result = progress(run_dir, manifest)
    print("finished: %d/%d batches, %d given up" % (result[0], result[2], result[1]), flush=True)
    return result


# ------------------------------------------------------------------------------------ collect

def collect(run_dir, loop=False, period=1800, max_seconds=82_800, token_file=None, batch=None):
    """Upload finished batches to <org>/<dataset>, folder data/<version>/. A loop keeps the
    files (generation is still running); a single pass deletes what it uploaded."""
    from reasoning_core.generation import collect as uploader
    manifest = load_manifest(run_dir)
    if token_file and not os.environ.get("HF_TOKEN"):
        os.environ["HF_TOKEN"] = Path(token_file).read_text().strip()
    lock = open(Path(run_dir) / "upload_state" / "collect.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(f"collect: another collector holds {run_dir}; exiting")
        return
    argv = ["--rc_path", str(run_dir), "--dataset_name", manifest["dataset"],
            "--version", manifest["version"], "--prefix", f"data/{manifest['version']}",
            "--no-delete" if loop else "--delete"]
    if batch:
        argv += ["--batch", str(batch)]
    deadline = time.time() + max_seconds
    while True:
        uploader.main(uploader.parse_args(argv))
        if not loop or time.time() + period > deadline:
            return
        time.sleep(period)


# ------------------------------------------------------------------------------------- submit

SKIP_DIRS = {"__pycache__", "deprecated", "generated", "task_search"}


def check_syntax(root=PACKAGE):
    """The G5K fleet runs Python 3.10: one newer-syntax file makes the package unimportable,
    and every node would die while the scheduler still shows the jobs as running. Generated
    tasks are left to init(), which imports each roster task under this same interpreter;
    walking their (large, untracked) trees on NFS takes minutes."""
    bad = []
    for dirpath, dirnames, filenames in os.walk(root):
        # only packages: run output (generated_data/, wandb/) can sit inside the tree
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS
                       and (Path(dirpath) / d / "__init__.py").exists()]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            path = Path(dirpath) / name
            try:
                ast.parse(path.read_bytes(), str(path))  # bytes: honours coding cookies
            except SyntaxError as e:
                bad.append(f"{path}:{e.lineno}: {e.msg}")
    if bad:
        raise SystemExit(f"does not parse under Python {sys.version.split()[0]}:\n  " + "\n  ".join(bad))


def _oarsub(oarsub, name, walltime, logs, command, array=None, dry_run=False):
    # OAR rejects '@' (in the Lille storage path) in -O/-E, so name the files relative to
    # the logs directory and submit from there.
    argv = [oarsub, "-n", name, "-t", "besteffort", "-t", "idempotent",
            "-l", f"/nodes=1,walltime={walltime}",
            "-O", f"{name}.%jobid%.out", "-E", f"{name}.%jobid%.err"]
    if array:
        argv += ["--array", str(array)]
    argv.append(command)
    print(f"$ cd {shlex.quote(str(logs))} && " + shlex.join(argv), flush=True)
    if dry_run:
        return None
    result = subprocess.run(argv, capture_output=True, text=True, cwd=logs)
    print(result.stdout + result.stderr, end="", flush=True)
    if result.returncode != 0 or "OAR_JOB_ID=" not in result.stdout:
        raise SystemExit(f"oarsub {name}: no job id (exit {result.returncode}); check oarstat before retrying")
    return result.stdout


def submit(run_dir, version, nodes=16, walltime="24:00:00", collect_walltime="24:00:00",
           smoke=False, home=None, token_file=None, oarsub="oarsub", dry_run=False, **init_settings):
    """Freeze the run, then queue `nodes` besteffort generate jobs and one looping collector."""
    run_dir = Path(run_dir)
    if smoke:
        version, run_dir = f"{version}-smoke", run_dir.with_name(run_dir.name + "-smoke")
        nodes, walltime = 1, "1:00:00"
        init_settings["rows_per_task"] = 2 * (init_settings.get("batch_size") or DEFAULTS["batch_size"])
    check_syntax()
    manifest = init(run_dir, version, **init_settings)
    logs = run_dir / "logs"
    env = f"HOME={shlex.quote(home)} " if home else ""
    prefix = (f"cd {shlex.quote(str(REPO))} && {env}PYTHONPATH={shlex.quote(str(REPO))} "
              f"{shlex.quote(sys.executable)} -m reasoning_core.generation")
    run = shlex.quote(str(run_dir))
    print(f"run {run_dir}: {len(manifest['tasks'])} tasks x {manifest['rows_per_task']} rows "
          f"on {nodes} nodes -> {manifest['dataset']}/data/{version}/", flush=True)
    _oarsub(oarsub, f"{version}_gen", walltime, logs, f"{prefix} generate --run-dir {run}",
            array=nodes, dry_run=dry_run)
    if not smoke:
        token = f" --token-file {shlex.quote(token_file)}" if token_file else ""
        _oarsub(oarsub, f"{version}_collect", collect_walltime, logs,
                f"{prefix} collect --run-dir {run} --loop{token}", dry_run=dry_run)
    print(f"when generation ends: {prefix} collect --run-dir {run}"
          + (f" --token-file {shlex.quote(token_file)}" if token_file else ""), flush=True)
    return run_dir
