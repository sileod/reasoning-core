#!/usr/bin/env python
"""Small parallel SFT planner for testing the experimental shared arm runner."""

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
    parser.add_argument("--experiment-id", default="run-sft-dev")
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    rows = [format_qa(q, a, tokenizer.eos_token) for q, a in (
        ("1 + 1?", "2"), ("2 + 2?", "4"), ("3 + 3?", "6"), ("4 + 4?", "8"),
    )]
    dataset = Dataset.from_list(rows)
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float32).to("cuda")
    spec = ArmSpec(
        experiment_id=args.experiment_id, arm_id="stage1", optimizer=args.optimizer,
        max_steps=args.steps, checkpoint_every_minutes=args.checkpoint_every_minutes,
        save_final=True,
    )
    _, metrics = train_arm(model, tokenizer, dataset, spec, eval_dataset=dataset)
    if metrics:
        record_event(spec, "stage_complete", metrics)
        print(metrics)


if __name__ == "__main__":
    main()
