"""The staging build end to end on this machine: init -> generate -> collect -> pile.

Only `oarsub` is faked; everything a Grid'5000 node runs is exercised for real."""
import json
import os
import stat
import subprocess
import sys
import time
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from reasoning_core.generation import build, collect, worker
from reasoning_core.generation.__main__ import main as cli

TASKS = ["arithmetics", "set_missing_element"]
REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def run(tmp_path):
    roster = tmp_path / "roster.txt"
    roster.write_text("# test roster\n" + "\n".join(TASKS) + "\n")
    run_dir = tmp_path / "run"
    build.init(run_dir, "rcT", roster=roster, rows_per_task=8, batch_size=4, levels=[0, 1])
    return run_dir


def rows(run_dir):
    return [json.loads(line) for f in sorted((run_dir / "generated_data" / "rcT").glob("*.jsonl"))
            for line in f.read_text().splitlines()]


def test_init_freezes_the_run_and_refuses_different_settings(run, tmp_path):
    manifest = build.load_manifest(run)
    assert manifest["tasks"] == TASKS and manifest["rows_per_task"] == 8
    assert build.init(run, "rcT", rows_per_task=8, git_rev=manifest["git"]) == manifest  # resubmit: no-op
    resumed = build.init(run, "rcT", git_rev="newer")  # newer code may resume, on the record
    assert resumed["resumed_at"] == ["newer"] and build.load_manifest(run)["resumed_at"] == ["newer"]
    with pytest.raises(SystemExit, match="different settings"):
        build.init(run, "rcT", rows_per_task=16)
    bad = tmp_path / "bad.txt"
    bad.write_text("no_such_task\n")
    with pytest.raises(SystemExit, match="does not resolve"):
        build.init(tmp_path / "other", "rcX", roster=bad)


def test_generate_writes_every_batch_and_no_cot_column(run):
    # lifetime=0 recycles each worker after one batch, exercising the restart path too
    done, failed, total = build.generate(run, workers=2, lifetime=0, report_every=3600)
    assert (done, failed, total) == (4, 0, 4)
    out = rows(run)
    assert len(out) == 16 and {r["task"] for r in out} == set(TASKS)
    assert all(set(r) == {"prompt", "answer", "metadata", "task"} for r in out)
    assert not list((run / "generated_data" / "rcT").glob("*.lock"))
    assert list((run / "logs").glob("*.batches.jsonl"))


def test_generate_resumes_and_respects_other_claims(run):
    out = run / "generated_data" / "rcT"
    (out / "arithmetics-0.jsonl").write_text("kept\n")          # finished earlier
    (out / "arithmetics-1.lock").touch()                        # held by a live node
    stale = out / "set_missing_element-0.lock"                  # left by a dead node
    stale.touch()
    os.utime(stale, (time.time() - build.STALE_LOCK_S - 1,) * 2)
    (out / "set_missing_element-1.fail").write_text("x" * build.MAX_ATTEMPTS)  # given up

    done, failed, _ = build.generate(run, workers=1, report_every=3600)

    assert (out / "arithmetics-0.jsonl").read_text() == "kept\n"
    assert not (out / "arithmetics-1.jsonl").exists()
    assert (out / "set_missing_element-0.jsonl").exists() and not stale.exists()
    assert not (out / "set_missing_element-1.jsonl").exists()
    assert (done, failed) == (2, 1)


def test_a_hung_batch_is_killed_and_eventually_given_up(run, monkeypatch):
    monkeypatch.setattr(worker, "run_task", lambda *a, **k: time.sleep(60))  # inherited by fork
    started = time.time()
    done, failed, total = build.generate(run, workers=2, batch_timeout=0.5, report_every=3600)
    assert (done, failed) == (0, total)
    assert time.time() - started < 45
    assert not list((run / "generated_data" / "rcT").glob("*.lock"))


def _spawn_helper(pids, then):
    """A generator that starts a helper in its own session, like the Lean REPL."""
    def run_task(name, idx, level, out, *a, **k):
        helper = subprocess.Popen(["sleep", "300"], start_new_session=True)
        with open(pids, "a") as f:
            f.write(f"{helper.pid}\n")
        return then(Path(out) / f"{name}-{idx}.jsonl")
    return run_task


def _alive(pids):
    import psutil
    return [int(p) for p in pids.read_text().split()
            if psutil.pid_exists(int(p)) and psutil.Process(int(p)).status() != psutil.STATUS_ZOMBIE]


@pytest.mark.parametrize("then, timeout", [
    (lambda path: (path.write_text("{}\\n"), (True, "ok"))[1], 1200),
    (lambda path: time.sleep(60), 0.5)])
def test_helpers_die_with_their_worker(run, monkeypatch, tmp_path, then, timeout):
    # recycled after each batch (lifetime=0), or killed mid-batch (timeout 0.5s)
    pids = tmp_path / "helpers"
    monkeypatch.setattr(worker, "run_task", _spawn_helper(pids, then))
    build.generate(run, workers=2, lifetime=0, batch_timeout=timeout, report_every=3600)
    assert pids.read_text() and not _alive(pids)


def test_a_worker_that_keeps_crashing_is_retired(run, monkeypatch):
    monkeypatch.setattr(worker, "run_task", lambda *a, **k: os._exit(3))
    done, _, _ = build.generate(run, workers=1, report_every=3600)  # must return, not spin
    assert done == 0


def test_collect_uploads_the_version_folder(run, monkeypatch):
    build.generate(run, workers=2, report_every=3600)
    uploaded = {}

    class Api:
        def create_repo(self, **kwargs): pass
        def file_exists(self, **kwargs): return False

    def upload(api, buf, remote, repo, msg):
        uploaded[remote] = (repo, pq.read_table(buf))

    monkeypatch.setattr(collect, "HfApi", Api)
    monkeypatch.setattr(collect, "upload_with_retry", upload)
    monkeypatch.setenv("HOME", str(run.parent))
    build.collect(run)

    [(remote, (repo, table))] = uploaded.items()
    assert repo == "reasoning-core/staging" and remote.startswith("data/rcT/shard-")
    assert table.num_rows == 16 and "cot" not in table.column_names
    assert not list((run / "generated_data" / "rcT").glob("*.jsonl"))  # single pass deletes


@pytest.fixture
def fake_oarsub(tmp_path):
    calls = tmp_path / "oarsub.calls"
    script = tmp_path / "oarsub"
    script.write_text(f"#!{sys.executable}\nimport json, os, sys\n"
                      f"open({str(calls)!r}, 'a').write(json.dumps(sys.argv[1:] + [os.getcwd()]) + '\\n')\n"
                      "print('OAR_JOB_ID=42')\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return script, calls


def test_submit_queues_a_besteffort_array_and_a_collector(tmp_path, fake_oarsub):
    oarsub, calls = fake_oarsub
    run_dir = tmp_path / "runs" / "rcT"
    cli(["submit", "--run-dir", str(run_dir), "--version", "rcT", "--nodes", "3",
         "--rows-per-task", "8", "--home", "/storage", "--token-file", "/storage/.hf_token",
         "--oarsub", str(oarsub)])
    gen, col = [json.loads(line) for line in calls.read_text().splitlines()]
    for argv in (gen, col):
        cwd = argv.pop()  # OAR rejects '@' in -O/-E paths: bare names, submitted from logs/
        assert cwd == str(run_dir / "logs") and "/" not in argv[argv.index("-O") + 1]
        assert argv.count("-t") == 2 and "besteffort" in argv and "idempotent" in argv
        assert f"--run-dir {run_dir}" in argv[-1] and "HOME=/storage" in argv[-1]
    assert gen[gen.index("--array") + 1] == "3" and " generate " in gen[-1]
    assert " collect " in col[-1] and "--loop" in col[-1] and "--token-file /storage/.hf_token" in col[-1]
    assert build.load_manifest(run_dir)["rows_per_task"] == 8


def test_smoke_submit_is_one_small_node_without_upload(tmp_path, fake_oarsub):
    oarsub, calls = fake_oarsub
    run_dir = tmp_path / "runs" / "rcT"
    cli(["submit", "--run-dir", str(run_dir), "--version", "rcT", "--smoke", "--oarsub", str(oarsub)])
    [gen] = [json.loads(line)[:-1] for line in calls.read_text().splitlines()]
    assert gen[gen.index("--array") + 1] == "1" and "walltime=1:00:00" in gen[gen.index("-l") + 1]
    manifest = build.load_manifest(tmp_path / "runs" / "rcT-smoke")
    assert manifest["version"] == "rcT-smoke" and manifest["rows_per_task"] == 2 * manifest["batch_size"]


def test_pile_builder_reads_a_run_and_keeps_every_row_instruct(run, tmp_path):
    build.generate(run, workers=2, report_every=3600)
    work = tmp_path / "pile"
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "rc_preprocess_upload.py"),
         "--source", str(run / "generated_data" / "rcT"), "--dry_run", "--test_ratio", "0",
         "--work_root", str(work), "--keep_work_dir", "--keep_output_shards"],
        capture_output=True, text=True, cwd=REPO, timeout=600)
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-2000:]
    tables = [pq.read_table(f) for f in work.glob("*/output/*.parquet")]
    modes = {m for t in tables for m in t["mode"].to_pylist()}
    assert sum(t.num_rows for t in tables) == 16 and modes == {"instruct"}
