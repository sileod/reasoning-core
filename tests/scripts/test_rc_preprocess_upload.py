from collections import defaultdict
from types import SimpleNamespace

import pytest

from scripts import rc_preprocess_upload as preprocess


class MemoryWriter:
    def __init__(self):
        self.rows = []

    def add(self, row):
        self.rows.append(dict(row))
        row.pop("_split")  # ShardWriter consumes this internal field.


@pytest.fixture
def args():
    return SimpleNamespace(
        seed=42, test_ratio=0.5, few_shot_ratio=1.0, cot_ratio=0.0,
        few_shot_pool_per_task=2,
    )


def item(row_i, split, args, task="alpha"):
    for nonce in range(1000):
        row = dict(
            task=task, prompt=f"Question {task}-{row_i}-{nonce}",
            answer=f"Answer {task}-{row_i}-{nonce}", metadata="{}",
            cot="", level=0, mode="instruct",
        )
        is_test = preprocess.stable_u01(
            row_i, row["prompt"], "test_split", seed=args.seed,
        ) < args.test_ratio
        if is_test == (split == "test"):
            return row_i, row, False
    raise AssertionError(f"Could not find a deterministic {split} row")


def process(batch, shot_pools, writer, args):
    return preprocess.process_transform_batch(
        batch, None, {}, shot_pools, writer, args,
    )


@pytest.mark.parametrize("separate_batches", [False, True])
def test_test_example_never_enters_training_demonstrations(args, separate_batches):
    held_out = item(0, "test", args)
    training = item(1, "train", args)
    shot_pools, writer = defaultdict(list), MemoryWriter()
    batches = [[held_out], [training]] if separate_batches else [[held_out, training]]

    for batch in batches:
        count, metrics = process(batch, shot_pools, writer, args)
        assert count == len(batch)
        assert not metrics

    test_out, train_out = writer.rows
    assert test_out["_split"] == "test"
    assert train_out["_split"] == "train"
    assert train_out["mode"] == "instruct"
    assert train_out["prompt"] == training[1]["prompt"]
    assert held_out[1]["prompt"] not in train_out["prompt"]
    assert held_out[1]["answer"] not in train_out["prompt"]
    assert shot_pools["alpha"] == [
        {key: training[1][key] for key in ("prompt", "answer")}
    ]


def test_training_example_supplies_demonstrations_to_both_splits(args):
    demonstration = item(0, "train", args)
    training = item(1, "train", args)
    held_out = item(2, "test", args)
    shot_pools, writer = defaultdict(list), MemoryWriter()

    process([demonstration, training, held_out], shot_pools, writer, args)

    assert writer.rows[0]["mode"] == "instruct"
    for output, source in zip(writer.rows[1:], [training, held_out]):
        assert output["mode"] == "few_shot"
        assert output["prompt"] == (
            f"{demonstration[1]['prompt']}\nAnswer:\n{demonstration[1]['answer']}"
            f"\n\n{source[1]['prompt']}\nAnswer:\n"
        )
    assert shot_pools["alpha"] == [
        {key: demonstration[1][key] for key in ("prompt", "answer")}
    ]


def test_only_training_rows_consume_per_task_pool_capacity(args):
    args.few_shot_ratio = 0.0
    shot_pools, writer = defaultdict(list), MemoryWriter()
    for task in ("alpha", "beta"):
        batch = [item(0, "test", args, task)]
        batch.extend(item(i, "train", args, task) for i in range(1, 4))
        process(batch, shot_pools, writer, args)
        assert shot_pools[task] == [
            {key: row[key] for key in ("prompt", "answer")}
            for _, row, _ in batch[1:3]
        ]
        assert len(shot_pools[task]) == args.few_shot_pool_per_task


@pytest.mark.parametrize("seed", [7, 42])
@pytest.mark.parametrize("mode", ["cot", "few_shot", "verification"])
def test_transformations_preserve_original_split_and_do_not_fill_pool(args, seed, mode):
    args.seed = seed
    args.cot_ratio = 1.0 if mode == "cot" else 0.0
    batch = []
    for row_i in range(12):
        _, row, _ = item(row_i, "test" if row_i % 2 else "train", args)
        row["cot"] = "A short derivation"
        batch.append((row_i, row, mode == "verification"))
    demonstration = {"prompt": "Training demonstration", "answer": "Reference answer"}
    shot_pools = defaultdict(list, alpha=[demonstration])
    writer = MemoryWriter()

    process(batch, shot_pools, writer, args)

    for output, (row_i, source, _) in zip(writer.rows, batch):
        expected = "test" if preprocess.stable_u01(
            row_i, source["prompt"], "test_split", seed=seed,
        ) < args.test_ratio else "train"
        assert output["_split"] == expected
        assert output["mode"] == mode
        assert output["prompt"] != source["prompt"]
    assert shot_pools["alpha"] == [demonstration]
