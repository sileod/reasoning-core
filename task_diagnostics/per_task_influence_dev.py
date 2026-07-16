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
from reasoning_core.training.dev_evals import (
    eval_id, evaluate_qa_nll, load_eval, load_qa_jsonl, save_eval,
)


def report_influence(spec, losses, identifier):
    delta = losses["treatment"] - losses["baseline"]
    reduction = -100 * delta / losses["baseline"]
    record_event(spec, "influence", {
        "eval_id": identifier, "delta_nll": delta, "reduction_pct": reduction,
    })
    result = {"losses": losses, "delta_nll": delta, "reduction_pct": reduction}
    print(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="sileod/microlm-ettin-swa-5m")
    parser.add_argument("--optimizer", choices=("adamw_torch", "prodigy", "adamc"),
                        default="adamw_torch")
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--seed", type=int, default=43)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
    parser.add_argument("--dtype", choices=("auto", "float32", "bfloat16"), default="auto")
    parser.add_argument("--checkpoint-every-minutes", type=float, default=60)
    parser.add_argument("--experiment-id", default="influence-dev")
    parser.add_argument("--format", choices=FORMATTERS, default="influence_legacy_v1")
    parser.add_argument("--main-source")
    parser.add_argument("--main-config")
    parser.add_argument("--aux-source")
    parser.add_argument("--aux-config")
    parser.add_argument("--aux-task", help="Optional task-column filter for a shared aux cache.")
    parser.add_argument("--mix-aux", type=float, default=0.2,
                        help="Absolute auxiliary fraction, matching production MIX_AUX.")
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--len-margin", type=int, default=8)
    parser.add_argument("--packing", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--prompt-prefix", default="")
    parser.add_argument("--eval-examples", type=int, default=16)
    parser.add_argument("--eval-jsonl",
                        help="Frozen {prompt,answer} JSONL scored with production QA-NLL.")
    parser.add_argument("--eval-name", default="shared_qa")
    parser.add_argument("--eval-limit", type=int)
    parser.add_argument("--arm", choices=("baseline", "treatment"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if bool(args.main_source) != bool(args.aux_source):
        parser.error("--main-source and --aux-source must be provided together")
    if not 0 < args.mix_aux < 1:
        parser.error("--mix-aux must be between 0 and 1")
    if args.len_margin < 0 or args.len_margin >= args.max_length:
        parser.error("--len-margin must be non-negative and smaller than --max-length")
    use_bf16 = args.dtype == "bfloat16" or (
        args.dtype == "auto" and torch.cuda.is_bf16_supported()
    )
    shared_eval_id = (
        eval_id(args.eval_name, args.eval_jsonl, args.eval_limit) if args.eval_jsonl else None
    )

    def make_spec(arm_id, treatment):
        return ArmSpec(
            experiment_id=args.experiment_id, arm_id=arm_id, model=args.model,
            optimizer=args.optimizer,
            learning_rate=args.learning_rate, weight_decay=args.weight_decay,
            lr_scheduler_type="linear" if args.optimizer == "adamw_torch" else "constant",
            max_steps=args.steps, batch_size=args.batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            checkpoint_every_minutes=args.checkpoint_every_minutes,
            formatter=args.format, aux_formatter=args.format if treatment else None,
            prompt_prefix=args.prompt_prefix,
            aux_prompt_prefix=args.prompt_prefix if treatment else "",
            main_source=args.main_source or "synthetic", main_config=args.main_config,
            aux_source=args.aux_source if treatment else None,
            aux_config=args.aux_config if treatment else None,
            aux_task=args.aux_task if treatment else None,
            aux_fraction=args.mix_aux if treatment else 0,
            max_length=args.max_length, packing=args.packing, seed=args.seed, bf16=use_bf16,
        )

    remote = args.main_source and any(
        not Path(source).expanduser().exists() for source in (args.main_source, args.aux_source)
    )
    if remote and args.arm is None:
        for arm in ("baseline", "treatment"):
            subprocess.run([sys.executable, __file__, *sys.argv[1:], "--arm", arm], check=True)
        losses = {}
        for arm in ("baseline", "treatment"):
            spec = make_spec(arm, arm == "treatment")
            if shared_eval_id:
                losses[arm] = load_eval(spec.run_dir, shared_eval_id)["nll"]
            else:
                status = json.loads((spec.run_dir / "status.json").read_text())
                losses[arm] = status["metrics"]["eval_loss"]
        spec = make_spec("treatment", True)
        report_influence(spec, losses, shared_eval_id or "dev/main_nll@v1")
        return

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    main_rows = [format_row(
        {"prompt": q, "answer": a}, tokenizer.eos_token, args.format, args.prompt_prefix,
    ) for q, a in (
        ("1 + 1?", "2"), ("2 + 2?", "4"), ("3 + 3?", "6"),
    )]
    task_rows = [format_row(
        {"prompt": "If A implies B and A is true, is B true?", "answer": "Yes"},
        tokenizer.eos_token, args.format, args.prompt_prefix,
    )]
    if args.main_source:
        main_spec = StreamSpec(
            args.main_source, args.format, config=args.main_config,
            prompt_prefix=args.prompt_prefix, cycle=True,
        )
        aux_spec = StreamSpec(
            args.aux_source, args.format, config=args.aux_config, cycle=True,
            prompt_prefix=args.prompt_prefix, task=args.aux_task,
        )
        eval_ds = Dataset.from_list(list(
            load_stream(main_spec, tokenizer).take(args.eval_examples)
        ))

        def arm_dataset(treatment):
            main = load_stream(main_spec, tokenizer)
            aux = (load_stream(
                aux_spec, tokenizer, args.max_length,
                max_tokens=args.max_length - args.len_margin,
            ) if treatment else None)
            return mix_streams(
                main, aux, args.mix_aux if treatment else 0,
                seed=args.seed, shuffle_buffer=0,
            )
    else:
        eval_ds = Dataset.from_list(main_rows)

        def arm_dataset(treatment):
            return Dataset.from_list(main_rows + (task_rows if treatment else []))

    torch.manual_seed(args.seed)
    dtype = torch.bfloat16 if use_bf16 else torch.float32
    template = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=dtype, attn_implementation="sdpa",
    ).to("cuda")
    initial = {k: v.detach().cpu().clone() for k, v in template.state_dict().items()}
    shared_examples = (
        load_qa_jsonl(args.eval_jsonl, tokenizer.eos_token, args.eval_limit)
        if shared_eval_id else None
    )
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
            record_event(spec, "arm_complete", metrics)
        if shared_eval_id:
            try:
                result = load_eval(spec.run_dir, shared_eval_id)
            except FileNotFoundError:
                if trainer is None:
                    raise RuntimeError(
                        f"{arm_id} predates eval {shared_eval_id}; use a new --experiment-id"
                    )
                result = evaluate_qa_nll(
                    template, tokenizer, shared_examples, args.max_length,
                )
                save_eval(spec.run_dir, shared_eval_id, result)
                record_event(spec, "evaluation", {
                    "eval_id": shared_eval_id,
                    **{key: value for key, value in result.items() if key != "per_example"},
                })
            losses[arm_id] = result["nll"]
        elif metrics:
            losses[arm_id] = metrics["eval_loss"]
        del trainer
        gc.collect()
    if args.arm is None and len(losses) == 2:
        report_influence(spec, losses, shared_eval_id or "dev/main_nll@v1")
    if remote:
        settle_remote_streams()


if __name__ == "__main__":
    main()
