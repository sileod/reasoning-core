"""End-to-end check of the RL environments and adapters in integrations/.

Each probe gets a fresh uv venv with its *latest* dependencies and is driven the way a
trainer drives it, with a stand-in policy answering gold or adversarial wrong answers:

  primeintellect  verifiers `load_environment` on the procedural pile -> `env.evaluate`
                  against a local fake OpenAI endpoint (rollout, parsing, rubric all real);
                  `--live-model` adds a real OpenRouter model on the eval rows
  openenv         the FastAPI server on the procedural pile, under uvicorn, driven
                  through the WebSocket client
  reasoning_gym   every roster task registered into reasoning-gym (fresh generation)
  collections     the reasoning-gym and SynLogic generators wrapped as core tasks

Checks: gold answers earn 1, wrong answers earn < 1, scorers never raise, every pile
task in the sample reaches the env, and one seed serves the same rows twice. The pile
revision is resolved to a commit SHA and recorded, so a report can be replayed:

    python scripts/check_rl_envs.py                         # local checkout, pile main
    python scripts/check_rl_envs.py --rc pypi --revision <sha from a previous report>
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import threading
import time
import zlib
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PILE = "reasoning-core/procedural-pile"
PYGGP = "978690ee0e6ccc7562f1ef1096c316a696ed4484"
ENVS = {  # what to install next to reasoning-core for each probe
    "primeintellect": [str(REPO / "integrations/primeintellect/reasoning_core_env")],
    "openenv": [str(REPO / "integrations/openenv/reasoning_core_env")],
    # generation, not just scoring: the game tasks need pyggp, which is git-only and so undeclared
    "reasoning_gym": ["reasoning-gym", f"pyggp @ git+https://github.com/Entze/pyggp@{PYGGP}"],
    "collections": ["reasoning-gym", "math-verify", "markdown"],  # markdown: SynLogic's verifiers
}
# adversarial wrong answers: each has broken at least one scorer (crash, NaN, or reward 1)
WRONGS = ["\x00x\x00", "", "zzz", "nan", "[[[[", "import os", "1" * 20000, "None"]


def wrong_answer(prompt: str) -> str:
    return WRONGS[zlib.crc32(prompt.encode()) % len(WRONGS)]


def gold_policy(answers: dict[str, str], wrong: bool):
    """Stand-in policy: the gold answer for a known prompt, or a wrong one."""
    def reply(prompt: str) -> str:
        return f"<think>.</think>\n<answer>{wrong_answer(prompt) if wrong else answers.get(prompt, '')}</answer>"
    return reply


def scorer_errors(rows: list[dict]) -> dict:
    """Score every WRONGS answer straight through reasoning_core: envs may swallow scorer exceptions as 0."""
    from reasoning_core import score_answer
    errors = {}
    for r in rows:
        for w in WRONGS:
            try:
                x = float(score_answer(w, {"task": r["task"], "answer": r["answer"], "metadata": r["metadata"]}))
                problem = None if 0 <= x <= 1 else f"reward {x}"
            except Exception as error:
                problem = f"{type(error).__name__}: {str(error)[:80]}"
            if problem:
                errors.setdefault(r["task"], {})[repr(w[:12])] = problem
    return errors


def summarize(rows: list[dict], rewards: list[float], wrong_rewards: list[float], pile_tasks: Counter) -> dict:
    """rows: task, prompt, answer, metadata (dict or JSON string)."""
    tasks = Counter(r["task"] for r in rows)
    bad = lambda x: x is None or not 0 <= x <= 1  # also catches NaN
    gold_fail = Counter(r["task"] for r, x in zip(rows, rewards) if bad(x) or x < 1)
    wrong_pass = Counter(r["task"] for r, x in zip(rows, wrong_rewards)
                         if (bad(x) or x >= 1) and wrong_answer(r["prompt"]).strip() != r["answer"].strip())
    return {
        "rows": len(rows),
        "tasks": len(tasks),
        "dropped_tasks": sorted(set(pile_tasks) - set(tasks)),
        "gold_reward_mean": sum(rewards) / max(len(rewards), 1),
        "gold_failures": dict(gold_fail),
        "wrong_reward_mean": sum(wrong_rewards) / max(len(wrong_rewards), 1),
        "wrong_passes": dict(wrong_pass),
        "scorer_errors": scorer_errors(rows),
    }


def pile_task_counts(split: str, n: int, seed: int, revision: str, buffer_size: int = 1000) -> Counter:
    """Tasks in the rows the env should have drawn (same stream, seed and buffer as the env)."""
    from datasets import load_dataset
    stream = load_dataset(PILE, split=split, streaming=True, revision=revision).shuffle(seed=seed, buffer_size=buffer_size)
    return Counter(r["task"] for r in stream.take(n))


# --------------------------------------------------------------------------- probes (run inside the env venv)

@contextmanager
def gold_endpoint(answers: dict[str, str]):
    """A local OpenAI-compatible endpoint replying `policy["reply"](prompt)`; yields (client, policy).

    policy["reply"] defaults to the gold answer; set it to gold_policy(answers, wrong=True) for wrong ones.
    """
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    policy = {"reply": gold_policy(answers, wrong=False), "misses": []}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            prompt = next(m["content"] for m in reversed(body["messages"]) if m["role"] == "user")
            if isinstance(prompt, list):
                prompt = "".join(part.get("text", "") for part in prompt)
            if prompt not in answers:
                policy["misses"].append(prompt[:300])
            out = json.dumps({
                "id": "x", "object": "chat.completion", "created": 0, "model": body["model"],
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": policy["reply"](prompt)}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

    class Server(ThreadingHTTPServer):
        request_queue_size = 1024  # the default backlog of 5 drops requests under evaluate()'s concurrency

    server = Server(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/v1"
    try:
        import verifiers as vf
        if tuple(map(int, vf.__version__.split(".")[:2])) >= (0, 3):  # 0.3 takes a ClientConfig
            os.environ.setdefault("RC_FAKE_KEY", "x")
            client = vf.ClientConfig(api_base_url=url, api_key_var="RC_FAKE_KEY", max_retries=0)
        else:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(base_url=url, api_key="x", max_retries=0)
        yield client, policy
    finally:
        server.shutdown()


def rollouts(env, client, model: str = "gold", **kwargs) -> list[dict]:
    """env.evaluate over its eval_dataset; one dict per rollout: reward, info, prompt (user text), completion."""
    evaluate = getattr(env, "evaluate_sync", env.evaluate)  # verifiers >= 0.3: evaluate is async
    out = evaluate(client=client, model=model, num_examples=kwargs.pop("num_examples", -1),
                   max_concurrent=kwargs.pop("max_concurrent", 32), **kwargs)
    get = lambda o, k: o[k] if isinstance(o, dict) else getattr(o, k)
    try:
        outputs = get(out, "outputs")
    except (KeyError, AttributeError):  # verifiers < 0.3: column-wise results
        outputs = [dict(zip(("reward", "info", "prompt", "completion"), r)) for r in
                   zip(*(get(out, k) for k in ("reward", "info", "prompt", "completion")))]
    text = lambda messages: next(m["content"] for m in reversed(messages) if m["role"] == "user")
    return [{"reward": get(o, "reward"), "info": get(o, "info"), "prompt": text(get(o, "prompt")),
             "completion": get(o, "completion")} for o in outputs]


def gold_and_wrong(env, answers: dict[str, str]) -> tuple[list[dict], list[float], list[float]]:
    """Rows (task, prompt, answer, metadata, completion) with gold and wrong rewards, in rollout order."""
    with gold_endpoint(answers) as (client, policy):
        gold = rollouts(env, client)
        policy["reply"] = gold_policy(answers, wrong=True)
        wrong = {r["prompt"]: r["reward"] for r in rollouts(env, client)}
    rows = [{**r["info"], "task": r["info"]["task_name"], "prompt": r["prompt"], "completion": r["completion"]}
            for r in gold]
    return rows, [r["reward"] for r in gold], [wrong[r["prompt"]] for r in rows]


def probe_primeintellect(n: int, seed: int, revision: str) -> dict:
    from reasoning_core_env import load_environment

    def load():
        return load_environment(num_train_examples=n, num_eval_examples=n, seed=seed, revision=revision)

    env, again = load(), load()
    same = all(list(d["question"]) == list(e["question"]) for d, e in
               ((env.dataset, again.dataset), (env.eval_dataset, again.eval_dataset)))
    answers = {q: a for d in (env.dataset, env.eval_dataset) for q, a in zip(d["question"], d["answer"])}

    report = {"deterministic": same}
    again.eval_dataset = again.dataset  # evaluate() runs on eval_dataset; aim the twin load at the train rows
    for split, split_env in (("train", again), ("test", env)):
        rows, rewards, wrong_rewards = gold_and_wrong(split_env, answers)
        report[split] = summarize(rows, rewards, wrong_rewards, pile_task_counts(split, n, seed, revision))
        report[split]["gold_failure_examples"] = [
            {"task": r["task"], "answer": r["answer"][:200], "completion": str(r["completion"])[:400], "reward": x}
            for r, x in zip(rows, rewards) if x is None or not x >= 1][:5]
    if os.getenv("RC_LIVE_MODEL"):
        report["live"] = live_eval(env, os.environ["RC_LIVE_MODEL"], int(os.getenv("RC_LIVE_N", "100")))
    return report


def openrouter_usage() -> float:
    import urllib.request
    request = urllib.request.Request("https://openrouter.ai/api/v1/key",
                                     headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    return json.load(urllib.request.urlopen(request, timeout=30))["data"]["usage"]


def live_eval(env, model: str, n: int) -> dict:
    """A real model through OpenRouter on the eval rows: checks prompt/answer formatting, not model quality."""
    import verifiers as vf
    usage = openrouter_usage()
    client = vf.ClientConfig(api_base_url="https://openrouter.ai/api/v1", api_key_var="OPENROUTER_API_KEY")
    evaluate = getattr(env, "evaluate_sync", env.evaluate)
    out = evaluate(client=client, model=model, num_examples=n, max_concurrent=16,
                   sampling_args={"max_tokens": 4096, "temperature": 0.0})
    outputs = out["outputs"] if isinstance(out, dict) else out.outputs
    get = lambda o, k: o[k] if isinstance(o, dict) else getattr(o, k)
    text = lambda o: str(get(o, "completion")[-1]["content"]) if get(o, "completion") else ""
    by_task = {}
    for o in outputs:
        by_task.setdefault(get(o, "info")["task_name"], []).append(get(o, "reward"))
    return {
        "model": model, "rows": len(outputs),
        "reward_mean": sum(get(o, "reward") for o in outputs) / max(len(outputs), 1),
        "answer_tag_rate": sum("<answer>" in text(o) for o in outputs) / max(len(outputs), 1),
        "empty_completions": sum(not text(o) for o in outputs),
        "reward_by_task": {t: round(sum(v) / len(v), 2) for t, v in sorted(by_task.items())},
        "cost_usd": round(openrouter_usage() - usage, 4),
    }


def probe_openenv(n: int, seed: int, revision: str) -> dict:
    from reasoning_core_env import ReasoningCoreAction, ReasoningCoreEnv

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "reasoning_core_env.server.app:app", "--port", str(port), "--log-level", "warning"],
        env={**os.environ, "RC_HF_REVISION": revision},
    )
    try:
        import urllib.request
        for _ in range(300):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1)
                break
            except OSError:
                time.sleep(1)
        url = f"http://127.0.0.1:{port}"
        report = {}
        for split in ("train", "test"):
            def session(answer):  # each WebSocket session gets its own env, serving rows from index 0
                with ReasoningCoreEnv(base_url=url).sync() as env:
                    for i in range(n):
                        obs = env.reset(split=split, seed=seed, size=n, revision=revision).observation
                        yield obs.prompt, env.step(ReasoningCoreAction(answer=answer(i, obs.prompt))).observation

            # the env reveals the gold answer after the step: a wrong pass first, then a gold replay
            wrong = list(session(lambda i, prompt: wrong_answer(prompt)))
            gold = list(session(lambda i, prompt: f"<answer>{wrong[i][1].correct_answer}</answer>"))
            rows = [{"task": o.task_name, "prompt": p, "answer": o.correct_answer, "metadata": o.dataset_metadata}
                    for p, o in wrong]
            report[split] = summarize(rows, [o.reward for _, o in gold], [o.reward for _, o in wrong],
                                      pile_task_counts(split, n, seed, revision, buffer_size=max(n * 4, 1000)))
            report[split]["deterministic"] = [p for p, _ in gold] == [p for p, _ in wrong]
        return report
    finally:
        server.terminate()
        server.wait()


def probe_reasoning_gym(n: int, seed: int, revision: str) -> dict:
    """Core tasks registered into reasoning-gym (fresh generation; the pile does not apply)."""
    import reasoning_gym
    from reasoning_core import list_tasks, register_to_reasoning_gym

    tasks = list_tasks()
    register_to_reasoning_gym(tasks)
    rows, gold, wrong, errors = [], [], [], {}
    per_task = max(1, n // len(tasks))
    for task in tasks:
        try:
            dataset = reasoning_gym.create_dataset(task, size=per_task, seed=seed)
            for entry in dataset:
                rows.append({"task": task, "prompt": entry["question"], "answer": entry["answer"], "metadata": entry["metadata"]})
                gold.append(dataset.score_answer(entry["answer"], entry))
                wrong.append(dataset.score_answer(wrong_answer(entry["question"]), entry))
        except Exception as error:
            errors[task] = f"{type(error).__name__}: {str(error)[:120]}"
    return {"generated": summarize(rows, gold, wrong, Counter(tasks)) | {"generation_errors": errors}}


def probe_collections(n: int, seed: int, revision: str) -> dict:
    """reasoning-gym and SynLogic generators wrapped as core tasks (fresh generation)."""
    import random

    from reasoning_core import get_task, score_answer
    from reasoning_core.integrations.reasoning_gym import RGYM_TASKS
    from reasoning_core.integrations.synlogic import usable_games

    random.seed(seed)
    report = {}
    for collection, key, subtasks in (("reasoning_gym", "rg_task", RGYM_TASKS), ("synlogic", "task", usable_games())):
        rows, gold, wrong, errors = [], [], [], {}
        for sub in subtasks:
            try:
                # a config attribute set beforehand does not survive generate_example(level=...)
                x = get_task(collection).generate_example(level=1, **{key: sub})
                scores = float(score_answer(x.answer, x)), float(score_answer(wrong_answer(x.prompt), x))
                rows.append({"task": sub, "prompt": x.prompt, "answer": str(x.answer), "metadata": x.metadata})
                gold.append(scores[0])
                wrong.append(scores[1])
            except Exception as error:
                errors[sub] = f"{type(error).__name__}: {str(error)[:120]}"
        summary = summarize(rows, gold, wrong, Counter(subtasks))
        summary.pop("scorer_errors")  # scorer_errors re-dispatches by row task; these rows dispatch by collection
        report[collection] = summary | {"generation_errors": errors}
    return report


PROBES = {"primeintellect": probe_primeintellect, "openenv": probe_openenv,
          "reasoning_gym": probe_reasoning_gym, "collections": probe_collections}


# --------------------------------------------------------------------------- driver

def versions(python: Path) -> dict:
    out = subprocess.run(["uv", "pip", "list", "--format", "json", "--python", str(python)],
                         capture_output=True, text=True, check=True).stdout
    keep = {"reasoning-core", "verifiers", "openenv", "openenv-core", "datasets", "fastapi"}
    return {p["name"]: p["version"] + (f" ({p['editable_project_location']})" if p.get("editable_project_location") else "")
            for p in json.loads(out) if p["name"] in keep}


def failures(report: dict) -> list[str]:
    bad = []
    for name, env in report["envs"].items():
        if "error" in env:
            bad.append(f"{name}: {env['error']}")
            continue
        for split, r in env.items():
            if not isinstance(r, dict) or "gold_failures" not in r:
                continue
            if r.get("generation_errors"):
                bad.append(f"{name}/{split}: generation failed for {r['generation_errors']}")
            if r["gold_failures"]:
                bad.append(f"{name}/{split}: gold answer < 1 for {r['gold_failures']}")
            if r["wrong_passes"]:
                bad.append(f"{name}/{split}: wrong answer = 1 (or invalid reward) for {r['wrong_passes']}")
            if r.get("scorer_errors"):
                bad.append(f"{name}/{split}: scorer raised or left [0, 1] on {r['scorer_errors']}")
            if r["dropped_tasks"]:
                bad.append(f"{name}/{split}: pile tasks never served {r['dropped_tasks']}")
            if not r.get("deterministic", env.get("deterministic", True)):
                bad.append(f"{name}/{split}: same seed served different rows")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--envs", nargs="+", default=list(ENVS), choices=list(ENVS))
    ap.add_argument("--rc", default="local", help="'local' (this checkout, editable), 'pypi', or a pip spec")
    ap.add_argument("--revision", help="pile revision (tag or SHA); default: resolve main to its SHA")
    ap.add_argument("--n", type=int, default=300, help="rows per split")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--venv-root", type=Path, default=Path(os.getenv("TMPDIR", "/tmp")) / "rc_env_check")
    ap.add_argument("--out", type=Path, help="write the JSON report here")
    ap.add_argument("--live-model", help="also run this OpenRouter model on the Prime env's eval rows "
                                         "(needs OPENROUTER_API_KEY)")
    ap.add_argument("--live-n", type=int, default=100)
    ap.add_argument("--probe", choices=list(ENVS), help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.probe:
        print("RESULT " + json.dumps(PROBES[args.probe](args.n, args.seed, args.revision)))
        return

    from huggingface_hub import HfApi
    revision = HfApi().dataset_info(PILE, revision=args.revision).sha
    rc = {"local": ["-e", str(REPO)], "pypi": ["reasoning-core"]}.get(args.rc, [args.rc])
    env = {"UV_CACHE_DIR": str(args.venv_root / "uv-cache"),  # local disk: NFS stalls uv for minutes
           "UV_PYTHON_INSTALL_DIR": str(args.venv_root / "uv-python"), **os.environ}
    if args.live_model:
        env |= {"RC_LIVE_MODEL": args.live_model, "RC_LIVE_N": str(args.live_n)}
    report = {"pile": PILE, "live_model": args.live_model, "revision": revision, "rc": args.rc, "n": args.n, "seed": args.seed,
              "commit": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
              "envs": {}}
    for name in args.envs:
        venv = args.venv_root / f"{name}-{args.rc.replace('/', '_')}"
        python = venv / "bin/python"
        print(f"[{name}] installing into {venv}", file=sys.stderr)
        # uv-managed Python ships its headers, so C extensions (reasoning-gym's pycosat) build anywhere
        subprocess.run(["uv", "venv", "-q", "--clear", "--managed-python", "-p", "3.11", str(venv)], check=True, env=env)
        subprocess.run(["uv", "pip", "install", "-q", "--python", str(python), "--upgrade", *ENVS[name], *rc],
                       check=True, env=env)
        print(f"[{name}] probing", file=sys.stderr)
        t = time.time()
        proc = subprocess.run([str(python), __file__, "--probe", name, "--n", str(args.n), "--seed", str(args.seed),
                               "--revision", revision], capture_output=True, text=True, env=env)
        result = next((json.loads(line[7:]) for line in proc.stdout.splitlines() if line.startswith("RESULT ")), None)
        report["envs"][name] = {"versions": versions(python), "seconds": round(time.time() - t),
                                **(result or {"error": proc.stderr.strip().splitlines()[-1:] or proc.returncode})}
        if result is None:
            print(proc.stderr[-4000:], file=sys.stderr)

    report["failures"] = failures(report)
    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text + "\n")
    print(text)
    sys.exit(1 if report["failures"] else 0)


if __name__ == "__main__":
    main()
