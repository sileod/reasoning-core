import argparse
import csv
import os
import sys

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# INSERT at position 0 so the local reasoning_core takes priority over
# any pip-installed version in site-packages (append() puts it last, which
# loses to an already-installed package).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reasoning_core.tasks.code_execution import (
    CodeRunnability,
    CodeExecution,
    CodeInputDeduction,
    Consolidation,
)

TASKS = {
    "CodeRunnability": CodeRunnability,
    "CodeExecution": CodeExecution,
    "CodeInputDeduction": CodeInputDeduction,
    "Consolidation": Consolidation,
}

# Consolidation generates slowly (~1-5 min/sample due to multi-program
# pipeline). Cap it so the eval doesn't run for hours.
TASK_SAMPLE_CAPS = {
    "Consolidation": 20,
}


def evaluate_model(model_path, task_trained_on, num_test_samples=100,
                   results_file="experiments/ablation_results.csv"):
    print(f"Loading model from {model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, device_map="auto", dtype=torch.bfloat16
    )
    model.eval()

    results = {}

    for eval_task_name, task_cls in TASKS.items():
        task_instance = task_cls()
        n_samples = min(num_test_samples, TASK_SAMPLE_CAPS.get(eval_task_name, num_test_samples))

        print(f"\nGenerating {n_samples} problems for {eval_task_name}...")
        try:
            # Use generate_balanced_batch: generates all problems up front,
            # respects balancing keys, and avoids the gramforge cls._instances
            # accumulation that slows down repeated generate() calls in a loop.
            problems = task_instance.generate_balanced_batch(batch_size=n_samples)
        except Exception as e:
            print(f"  {eval_task_name}: generation failed — {e}")
            results[eval_task_name] = 0.0
            continue

        correct = 0
        pbar = tqdm(problems, desc=f"Eval {eval_task_name}", unit="sample")
        for ex in pbar:
            try:
                chat = [{"role": "user", "content": ex.prompt}]
                prompt_text = tokenizer.apply_chat_template(
                    chat, tokenize=False, add_generation_prompt=True
                )
                inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=128,
                        do_sample=False,
                        pad_token_id=tokenizer.eos_token_id,
                    )

                gen_text = tokenizer.decode(
                    outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True
                ).strip()

                score = task_instance.score_answer(gen_text, ex)
                correct += score
                pbar.set_postfix(acc=f"{correct / pbar.n:.2%}")
            except Exception:
                continue

        accuracy = correct / len(problems) if problems else 0.0
        results[eval_task_name] = accuracy
        print(f"  {eval_task_name}: {accuracy:.2%}")

    os.makedirs(os.path.dirname(results_file) if os.path.dirname(results_file) else ".", exist_ok=True)
    file_exists = os.path.isfile(results_file)
    with open(results_file, mode='a', newline='') as f:
        fieldnames = [
            'Trained_On_Task',
            'Eval_CodeRunnability',
            'Eval_CodeExecution',
            'Eval_CodeInputDeduction',
            'Eval_Consolidation',
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'Trained_On_Task': task_trained_on,
            'Eval_CodeRunnability': results.get('CodeRunnability', 0.0),
            'Eval_CodeExecution': results.get('CodeExecution', 0.0),
            'Eval_CodeInputDeduction': results.get('CodeInputDeduction', 0.0),
            'Eval_Consolidation': results.get('Consolidation', 0.0),
        })
    print(f"\nResults appended to {results_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=str, required=True)
    parser.add_argument("--trained_task", type=str, required=True)
    parser.add_argument("--samples", type=int, default=100)
    args = parser.parse_args()
    evaluate_model(args.model_dir, args.trained_task, args.samples)