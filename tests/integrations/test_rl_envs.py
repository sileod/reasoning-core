"""Offline, deterministic checks of the RL environments on a pinned sample of the procedural pile.

The fixture holds two rows per pile task, taken from one pile revision, so these tests need
no network and do not move when the pile does. `scripts/check_rl_envs.py` is the slow
counterpart: fresh venvs, latest dependencies, live data. Refresh the fixture after a pile
release with `python tests/integrations/test_rl_envs.py <revision>`.
"""
import gzip
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from reasoning_core import get_score_answer_fn, score_answer

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("data") / "pile_sample.jsonl.gz"


def load_by_path(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROWS = [json.loads(line) for line in gzip.open(FIXTURE, "rt")] if FIXTURE.exists() else []
IDS = [f"{row['task']}-{i % 2}" for i, row in enumerate(ROWS)]

# by path: a top-level `scripts` package from another install can shadow this repo's scripts/
check = load_by_path("check_rl_envs", "scripts/check_rl_envs.py")
PILE, WRONGS, gold_and_wrong, wrong_answer = check.PILE, check.WRONGS, check.gold_and_wrong, check.wrong_answer


def test_fixture_is_pinned_and_covers_every_task():
    assert {row["revision"] for row in ROWS} == {ROWS[0]["revision"]}
    assert len({row["task"] for row in ROWS}) >= 50


@pytest.mark.parametrize("task", sorted({row["task"] for row in ROWS}))
def test_every_pile_task_has_a_scorer_with_core_dependencies(task):
    # an env silently skips rows it cannot score: pyggp once hid both game tasks this way
    get_score_answer_fn(task)


@pytest.mark.parametrize("row", ROWS, ids=IDS)
def test_gold_scores_one_and_wrong_answers_score_below_one(row):
    assert score_answer(row["answer"], row) == 1
    for wrong in WRONGS:
        score = float(score_answer(wrong, row))  # must not raise
        assert 0 <= score <= 1, (wrong, score)  # NaN fails here too
        assert score < 1 or wrong.strip() == row["answer"].strip(), wrong


def test_prime_env_rollouts_reward_gold_and_only_gold():
    pytest.importorskip("verifiers")
    from datasets import Dataset, DatasetDict

    module = load_by_path("pi_reasoning_core_env", "integrations/primeintellect/reasoning_core_env/reasoning_core_env.py")
    data = Dataset.from_list([{k: row[k] for k in ("task", "prompt", "answer", "metadata")} for row in ROWS])
    env = module.rc_ds_to_env(DatasetDict(train=data, test=data))
    assert len(env.eval_dataset) == len(ROWS)

    rows, gold, wrong = gold_and_wrong(env, dict(zip(env.eval_dataset["question"], env.eval_dataset["answer"])))
    assert {r["task"] for r, x in zip(rows, gold) if x != 1} == set()
    assert {r["task"] for r, x in zip(rows, wrong) if x >= 1 and r["answer"].strip() not in WRONGS} == set()


def test_openenv_episodes_reward_gold_and_only_gold(monkeypatch):
    pytest.importorskip("openenv")
    sys.path.insert(0, str(ROOT / "integrations/openenv/reasoning_core_env"))
    from models import ReasoningCoreAction
    from server import reasoning_core_environment as module

    entries = [e for i, row in enumerate(ROWS) if (e := module._normalize_entry(row, i))]
    assert len(entries) == len(ROWS)
    monkeypatch.setattr(module, "_load_hub_entries", lambda *args: entries)

    env = module.ReasoningCoreEnvironment()
    for row in ROWS:
        assert env.reset().prompt == row["prompt"]
        assert env.step(ReasoningCoreAction(answer=f"<answer>{row['answer']}</answer>")).reward == 1
    for row in ROWS:
        env.reset()
        wrong = wrong_answer(row["prompt"])
        assert env.step(ReasoningCoreAction(answer=wrong)).reward < 1 or wrong == row["answer"]


if __name__ == "__main__":  # refresh the fixture: python tests/integrations/test_rl_envs.py <revision>
    from datasets import load_dataset
    from huggingface_hub import HfApi

    revision = HfApi().dataset_info(PILE, revision=sys.argv[1] if len(sys.argv) > 1 else None).sha
    picked = {}
    stream = load_dataset(PILE, split="test", streaming=True, revision=revision).shuffle(seed=0, buffer_size=30000)
    for row in stream.take(30000):
        if len(picked.setdefault(row["task"], [])) < 2:
            picked[row["task"]].append(row | {"revision": revision})
    FIXTURE.parent.mkdir(exist_ok=True)
    lines = "".join(json.dumps(row) + "\n" for task in sorted(picked) for row in picked[task])
    with open(FIXTURE, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as out:  # mtime=0: same bytes
        out.write(lines.encode())
    print(f"{sum(map(len, picked.values()))} rows, {len(picked)} tasks, revision {revision} -> {FIXTURE}")
