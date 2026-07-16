#!/usr/bin/env python
"""Small parallel influence planner for testing paired arms on the shared dev runner."""

import argparse
import gc
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from reasoning_core.training.paths import configure_runtime_env

configure_runtime_env()

import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from reasoning_core.training.dev_data import (
    FORMATTERS, StreamSpec, format_row, load_stream, mix_streams, settle_remote_streams,
)
from reasoning_core.training.dev_engine import ArmSpec, record_event, train_arm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="sileod/microlm-ettin-swa-5m")
    parser.add_argument("--optimizer", choices=("prodigy", "adamc"), default="prodigy")
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--checkpoint-every-minutes", type=float, default=60)
    parser.add_argument("--experiment-id", default="influence-dev")
    parser.add_argument("--format", choices=FORMATTERS, default="influence_legacy_v1")
    parser.add_argument("--main-source")
    parser.add_argument("--main-config")
    parser.add_argument("--aux-source")
    parser.add_argument("--aux-config")
    parser.add_argument("--aux-ratio", type=float, default=0.2)
    parser.add_argument("--eval-examples", type=int, default=16)
    parser.add_argument("--arm", choices=("baseline", "treatment"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if bool(args.main_source) != bool(args.aux_source):
        parser.error("--main-source and --aux-source must be provided together")

    def make_spec(arm_id, treatment):
        return ArmSpec(
            experiment_id=args.experiment_id, arm_id=arm_id, optimizer=args.optimizer,
            max_steps=args.steps, checkpoint_every_minutes=args.checkpoint_every_minutes,
            formatter=args.format, aux_formatter=args.format if treatment else None,
            main_source=args.main_source or "synthetic",
            aux_source=args.aux_source if treatment else None,
            aux_ratio=args.aux_ratio if treatment else 0,
        )

    remote = args.main_source and any(
        not Path(source).expanduser().exists() for source in (args.main_source, args.aux_source)
    )
    if remote and args.arm is None:
        for arm in ("baseline", "treatment"):
            subprocess.run([sys.executable, __file__, *sys.argv[1:], "--arm", arm], check=True)
        losses = {}
        for arm in ("baseline", "treatment"):
            status = json.loads(
                (make_spec(arm, arm == "treatment").run_dir / "status.json").read_text()
            )
            losses[arm] = status["metrics"]["eval_loss"]
        spec = make_spec("treatment", True)
        delta = losses["treatment"] - losses["baseline"]
        record_event(spec, "influence", {"eval_id": "dev/main_nll@v1", "delta": delta})
        print({"losses": losses, "delta": delta})
        return

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    main_rows = [format_row({"prompt": q, "answer": a}, tokenizer.eos_token, args.format) for q, a in (
        ("1 + 1?", "2"), ("2 + 2?", "4"), ("3 + 3?", "6"),
    )]
    task_rows = [format_row(
        {"prompt": "If A implies B and A is true, is B true?", "answer": "Yes"},
        tokenizer.eos_token, args.format,
    )]
    if args.main_source:
        main_spec = StreamSpec(args.main_source, args.format, config=args.main_config)
        aux_spec = StreamSpec(args.aux_source, args.format, config=args.aux_config, cycle=True)
        eval_ds = Dataset.from_list(list(load_stream(main_spec, tokenizer, 128).take(args.eval_examples)))

        def arm_dataset(treatment):
            main = load_stream(main_spec, tokenizer, 128)
            aux = load_stream(aux_spec, tokenizer, 128) if treatment else None
            return mix_streams(main, aux, args.aux_ratio if treatment else 0)
    else:
        eval_ds = Dataset.from_list(main_rows)

        def arm_dataset(treatment):
            return Dataset.from_list(main_rows + (task_rows if treatment else []))

    template = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float32).to("cuda")
    initial = {k: v.detach().cpu().clone() for k, v in template.state_dict().items()}
    losses = {}
    arms = ((args.arm, args.arm == "treatment"),) if args.arm else (
        ("baseline", False), ("treatment", True),
    )
    for arm_id, treatment in arms:
        template.load_state_dict(initial)
        spec = make_spec(arm_id, treatment)
        trainer, metrics = train_arm(
            template, tokenizer, arm_dataset(treatment), spec, eval_dataset=eval_ds,
        )
        if metrics:
            losses[arm_id] = metrics["eval_loss"]
            record_event(spec, "arm_complete", metrics)
        del trainer
        gc.collect()
    if args.arm is None and len(losses) == 2:
        delta = losses["treatment"] - losses["baseline"]
        record_event(spec, "influence", {"eval_id": "dev/main_nll@v1", "delta": delta})
        print({"losses": losses, "delta": delta})
    if remote:
        settle_remote_streams()


if __name__ == "__main__":
    main()
