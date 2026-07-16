#!/usr/bin/env python
"""Small parallel influence planner for testing paired arms on the shared dev runner."""

import argparse
import sys

sys.dont_write_bytecode = True

from reasoning_core.training.paths import configure_runtime_env

configure_runtime_env()

import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from reasoning_core.training.dev_engine import ArmSpec, format_qa, record_event, train_arm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="sileod/microlm-ettin-swa-5m")
    parser.add_argument("--optimizer", choices=("prodigy", "adamc"), default="prodigy")
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--checkpoint-every-minutes", type=float, default=60)
    parser.add_argument("--experiment-id", default="influence-dev")
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    main_rows = [format_qa(q, a, tokenizer.eos_token) for q, a in (
        ("1 + 1?", "2"), ("2 + 2?", "4"), ("3 + 3?", "6"),
    )]
    task_rows = [format_qa("If A implies B and A is true, is B true?", "Yes", tokenizer.eos_token)]
    eval_ds = Dataset.from_list(main_rows)

    template = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float32).to("cuda")
    initial = {k: v.detach().cpu().clone() for k, v in template.state_dict().items()}
    losses = {}
    for arm_id, rows in (("baseline", main_rows), ("task=logic_nli", main_rows + task_rows)):
        template.load_state_dict(initial)
        spec = ArmSpec(
            experiment_id=args.experiment_id, arm_id=arm_id, optimizer=args.optimizer,
            max_steps=args.steps, checkpoint_every_minutes=args.checkpoint_every_minutes,
        )
        _, metrics = train_arm(template, tokenizer, Dataset.from_list(rows), spec, eval_dataset=eval_ds)
        if metrics:
            losses[arm_id] = metrics["eval_loss"]
            record_event(spec, "arm_complete", metrics)
    if len(losses) == 2:
        delta = losses["task=logic_nli"] - losses["baseline"]
        record_event(spec, "influence", {"eval_id": "dev/main_nll@v1", "delta": delta})
        print({"losses": losses, "delta": delta})


if __name__ == "__main__":
    main()
