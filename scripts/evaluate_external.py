#!/usr/bin/env python
"""Evaluate a fine-tuned checkpoint on HumanEval (pass@k) and CRUXEval (I+O).

Kept separate from evaluate.py (which checks accuracy on the synthetic
reasoning-core tasks themselves) because these are the *external* downstream
benchmarks used to judge whether a synthetic task actually transfers.

Appends one row per run to a CSV so run_ablation.sh can call this once per
trained checkpoint (including the no-aux `baseline` arm) and
summarize_external_results.py can compute deltas against that baseline.
"""
import argparse
import ast
import csv
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scoring_core import (  # noqa: E402
    entry_point_name,
    pass_at_k,
    score_cruxeval_input,
    score_cruxeval_output,
    score_humaneval_completion,
    strip_code_fence,
)


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def generate_completions(model, tokenizer, prompt_text, n, max_new_tokens, temperature):
    """n completions for one prompt. Greedy (deterministic) when n == 1 and
    temperature == 0; sampled otherwise, since pass@k requires diverse
    samples to be a meaningful estimate rather than n identical copies."""
    chat = [{"role": "user", "content": prompt_text}]
    text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    gen_kwargs = dict(
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.eos_token_id,
        num_return_sequences=n,
    )
    if n == 1 and temperature == 0:
        gen_kwargs["do_sample"] = False
    else:
        gen_kwargs.update(do_sample=True, temperature=max(temperature, 1e-4), top_p=0.95)

    with torch.no_grad():
        out = model.generate(**inputs, **gen_kwargs)

    prompt_len = inputs.input_ids.shape[1]
    return [
        tokenizer.decode(row[prompt_len:], skip_special_tokens=True)
        for row in out
    ]


def evaluate_humaneval(model, tokenizer, n_samples, ks, max_new_tokens, temperature, timeout, limit=None):
    ds = load_dataset("openai/openai_humaneval")["test"]
    if limit:
        ds = ds.select(range(min(limit, len(ds))))

    per_problem = []  # list of (n, c)
    for i, ex in enumerate(ds):
        prompt_text = (
            "Complete the following Python function. Return ONLY the "
            "continuation of the function body, no explanation, no markdown "
            "fences, no repetition of the signature.\n\n"
            f"```python\n{ex['prompt']}\n```"
        )
        completions = generate_completions(model, tokenizer, prompt_text, n_samples, max_new_tokens, temperature)
        c = sum(
            score_humaneval_completion(ex["prompt"], comp, ex["test"], ex["entry_point"], timeout)
            for comp in completions
        )
        per_problem.append((n_samples, c))
        print(f"  humaneval {i + 1}/{len(ds)} ({ex['entry_point']}): {c}/{n_samples} passed", flush=True)

    result = {"n_problems": len(per_problem)}
    for k in ks:
        if k > n_samples:
            continue
        result[f"pass@{k}"] = mean(pass_at_k(n, c, k) for n, c in per_problem)
    return result


def evaluate_cruxeval(model, tokenizer, n_samples, max_new_tokens, temperature, timeout, limit=None):
    ds = load_dataset("cruxeval-org/cruxeval")["test"]
    if limit:
        ds = ds.select(range(min(limit, len(ds))))

    acc_o, acc_i = [], []
    for i, ex in enumerate(ds):
        code, call_input, true_output = ex["code"], ex["input"], ex["output"]
        try:
            fn = entry_point_name(code)
        except Exception:
            continue
        call_expr = call_input if call_input.strip().startswith(fn) else f"{fn}({call_input})"

        # --- CRUXEval-O: given code + the call, predict the return value ---
        prompt_o = (
            "Read the Python function below, then state the exact value "
            f"returned by the call `{call_expr}`. Answer with ONLY the "
            "Python literal value, nothing else.\n\n"
            f"```python\n{code}\n```\n\nCall: `{call_expr}`"
        )
        comp_o = generate_completions(model, tokenizer, prompt_o, n_samples, max_new_tokens, temperature)[0]
        ok_o = score_cruxeval_output(comp_o, true_output)
        acc_o.append(1.0 if ok_o else 0.0)

        # --- CRUXEval-I: given code + the output, predict a call producing it ---
        prompt_i = (
            "Read the Python function below. Find any input such that "
            f"calling it returns exactly: {true_output}\n"
            f"Answer with ONLY a full call expression like `{fn}(...)`, "
            "nothing else.\n\n"
            f"```python\n{code}\n```"
        )
        comp_i = generate_completions(model, tokenizer, prompt_i, n_samples, max_new_tokens, temperature)[0]
        ok_i = score_cruxeval_input(code, comp_i, true_output, timeout)
        acc_i.append(1.0 if ok_i else 0.0)

        print(f"  cruxeval {i + 1}/{len(ds)} ({fn}): O={'ok' if ok_o else 'no'} I={'ok' if ok_i else 'no'}", flush=True)

    return {
        "cruxeval_o_acc": mean(acc_o),
        "cruxeval_i_acc": mean(acc_i),
        "n_problems": len(acc_o),
    }


def write_row(csv_path, row):
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    existing_rows = []
    fieldnames = list(row.keys())
    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            existing_rows = list(reader)
            for name in reader.fieldnames or []:
                if name not in fieldnames:
                    fieldnames.append(name)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in existing_rows:
            writer.writerow(r)
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model_dir", required=True)
    parser.add_argument("--trained_task", required=True,
                         help="Label for this run, e.g. 'baseline', 'all', 'Consolidation'.")
    parser.add_argument("--humaneval_n", type=int, default=20,
                         help="Completions sampled per HumanEval problem (pool size for pass@k).")
    parser.add_argument("--humaneval_k", type=int, nargs="+", default=[1, 5, 10],
                         help="Which pass@k values to report (each must be <= humaneval_n).")
    parser.add_argument("--humaneval_temperature", type=float, default=0.8)
    parser.add_argument("--humaneval_limit", type=int, default=None,
                         help="Optional cap on number of HumanEval problems, for smoke tests.")
    parser.add_argument("--cruxeval_n", type=int, default=1,
                         help="Completions per CRUXEval problem per direction (I and O each).")
    parser.add_argument("--cruxeval_temperature", type=float, default=0.0)
    parser.add_argument("--cruxeval_limit", type=int, default=None)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--results_file", default="experiments/external_eval_results.csv")
    args = parser.parse_args()

    print(f"Loading model from {args.model_dir}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model_dir, device_map="auto", torch_dtype=torch.bfloat16)
    model.eval()

    t0 = time.time()
    print("Evaluating HumanEval...", flush=True)
    he = evaluate_humaneval(
        model, tokenizer, args.humaneval_n, args.humaneval_k,
        args.max_new_tokens, args.humaneval_temperature, args.timeout, args.humaneval_limit,
    )

    print("Evaluating CRUXEval...", flush=True)
    cx = evaluate_cruxeval(
        model, tokenizer, args.cruxeval_n,
        args.max_new_tokens, args.cruxeval_temperature, args.timeout, args.cruxeval_limit,
    )

    row = {
        "trained_task": args.trained_task,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.time() - t0, 1),
        **{f"humaneval_{k}": v for k, v in he.items()},
        **cx,
    }
    write_row(args.results_file, row)
    print(f"Wrote results to {args.results_file}")
    for k, v in row.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()