import importlib.util
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace


path = Path(__file__).parents[2] / "scripts/rc_preprocess_upload.py"
spec = importlib.util.spec_from_file_location("rc_preprocess_upload", path)
pre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pre)

ARGS = SimpleNamespace(seed=42, test_ratio=0.5, few_shot_ratio=1.0, few_shot_pool_per_task=8, cot_ratio=0)


class Writer:
    def __init__(self):
        self.rows = []

    def add(self, row):
        self.rows.append(dict(row))


def split_of(i, prompt):
    return "test" if pre.stable_u01(i, prompt, "test_split", seed=ARGS.seed) < ARGS.test_ratio else "train"


def first(split, start=0):
    i = start
    while split_of(i, f"<prompt {i}>") != split:
        i += 1
    return i


def run(indices):
    batch = [(i, {"task": "t", "mode": "instruct", "prompt": f"<prompt {i}>", "answer": f"<answer {i}>"}, False)
             for i in indices]
    writer, pools = Writer(), defaultdict(list)
    pre.process_transform_batch(batch, None, {}, pools, writer, ARGS)
    return writer.rows, pools


def test_test_rows_never_become_training_demonstrations():
    t = first("test")
    later = [i for i in range(t + 1, t + 200) if split_of(i, f"<prompt {i}>") == "train"]
    rows, pools = run([t, *later])
    assert all(s["prompt"] != f"<prompt {t}>" for s in pools["t"])
    for row in rows:
        if row["_split"] == "train":
            assert f"<prompt {t}>" not in row["prompt"] and f"<answer {t}>" not in row["prompt"]


def test_training_rows_still_supply_demonstrations():
    a = first("train")
    later = [i for i in range(a + 1, a + 200) if split_of(i, f"<prompt {i}>") == "train"]
    rows, pools = run([a, *later])
    assert pools["t"] and len(pools["t"]) <= ARGS.few_shot_pool_per_task
    assert any(row["mode"] == "few_shot" for row in rows)
