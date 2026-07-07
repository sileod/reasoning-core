import json
from collections import defaultdict

import torch
import wandb
from datasets import load_dataset

from reasoning_core import score_answer
from reasoning_core.template import Entry


def load_intrinsic_eval_split(path, skip=100_000, max_groups=200, max_examples_per_group=8, max_scanned=50_000):
    buckets = defaultdict(list)
    for i, row in enumerate(load_dataset(path, split="train", streaming=True).skip(skip)):
        if i >= max_scanned or (len(buckets) >= max_groups and all(len(v) >= max_examples_per_group for v in buckets.values())):
            break
        metadata = _metadata(row)
        task = _task(row, metadata)
        level = row.get("level", metadata.get("_level", ""))
        if not (task and level != "" and row.get("prompt") and row.get("answer")):
            continue
        group = ".".join(_key(v) for v in (task, level))
        if group not in buckets and len(buckets) >= max_groups:
            continue
        if len(buckets[group]) < max_examples_per_group:
            metadata.setdefault("_task", row.get("task") or metadata.get("task") or task)
            metadata.setdefault("_level", level)
            buckets[group].append({"prompt": row["prompt"], "answer": row["answer"], "metadata": metadata})
    print(f"intrinsic eval buckets ({len(buckets)} kept): {sorted((k, len(v)) for k, v in buckets.items())}")
    return dict(buckets)


def log_intrinsic_task_rewards(model, tokenizer, splits, sink, global_step=None, max_steps=None, max_new_tokens=64):
    metrics, by_task = {}, defaultdict(list)
    for group, rows in splits.items():
        vals = [_reward(model, tokenizer, row, max_new_tokens) for row in rows]
        if vals:
            task = group.rsplit(".", 1)[0]
            metrics[f"intrinsic_reward_tl/{group}"] = sum(vals) / len(vals)
            by_task[task].extend(vals)
    for task, vals in by_task.items():
        metrics[f"intrinsic_reward/{task}"] = sum(vals) / len(vals)
    metrics["intrinsic_eval/n"] = sum(map(len, by_task.values()))
    wandb.log(metrics, step=global_step) if global_step is not None else wandb.log(metrics)
    for key, value in metrics.items():
        if key.startswith("intrinsic_reward/"):
            wandb.run.summary[f"compare/{key.replace('/', '_')}"] = value
    sink.record(metrics, kind="intrinsic", global_step=global_step, max_steps=max_steps)


def _reward(model, tokenizer, row, max_new_tokens):
    prompt = f"Q: {row['prompt']}\nA:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tokenizer.eos_token_id)
    pred = tokenizer.decode(out[0, inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
    return float(score_answer(pred, Entry(metadata=row["metadata"], answer=row["answer"])))


def _metadata(row):
    metadata = row.get("metadata") or {}
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            metadata = {}
    return dict(metadata) if isinstance(metadata, dict) else {}


def _task(row, metadata):
    return (
        metadata.get("source_dataset")
        or metadata.get("task_name")
        or metadata.get("rg_task")
        or row.get("task")
        or metadata.get("_task")
        or metadata.get("task")
    )


def _key(x):
    return str(x).lower().replace("/", "_").replace(" ", "_").replace(".", "_")[:60]
