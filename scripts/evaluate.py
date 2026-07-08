import argparse
import csv
import os
import sys
from types import SimpleNamespace

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# INSERT at position 0 so the local reasoning_core beats any pip-installed version
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reasoning_core.tasks.code_execution import (
    CodeRunnability,
    CodeExecution,
    CodeInputDeduction,
    Consolidation,
    ConsolidationConfig,
)

# Difficulty levels — matches data_generation.py so eval and training are aligned
LEVELS = [0, 1, 2]

# Standard tasks: use generate_balanced_batch (fast, template-managed)
TASKS_STANDARD = {
    "CodeRunnability": CodeRunnability,
    "CodeExecution": CodeExecution,
    "CodeInputDeduction": CodeInputDeduction,
}

# Consolidation: must bypass template.py's SIGALRM timeout (fires during slow
# gramforge generation). We call generate() directly and wrap results manually.
CONSOLIDATION_SAMPLES_PER_LEVEL = 10   # 30 total across 3 levels (~1 hour)


def _make_consolidation_task(level=0):
    cfg = ConsolidationConfig(timeout=1.0, max_attempts=300, n_programs=3)
    task = Consolidation(config=cfg)
    task.config.set_level(level)
    return task


def _generate_consolidation_problems(level, n_samples):
    """Generate Consolidation problems at a given difficulty level.
    Calls generate() directly — bypasses template.py SIGALRM wrapper which
    fires too early for Consolidation's slow multi-program pipeline."""
    task_instance = _make_consolidation_task(level)
    problems = []
    attempts = 0
    max_attempts = n_samples * 20
    pbar = tqdm(total=n_samples, desc=f"Consolidation level={level}", unit="problem")
    while len(problems) < n_samples and attempts < max_attempts:
        attempts += 1
        try:
            problem = task_instance.generate()
            ex = SimpleNamespace(
                prompt=task_instance.prompt(problem.metadata),
                answer=problem.answer,
                metadata=problem.metadata,
                _task=task_instance,
            )
            problems.append(ex)
            pbar.update(1)
        except BaseException:
            # Catch both Exception and BaseException (TimeoutException from template)
            continue
    pbar.close()
    return problems, task_instance


def score_generation(model, tokenizer, problems, task_instance, desc):
    """Run model inference on a list of problems and return total correct."""
    correct = 0
    pbar = tqdm(problems, desc=desc, unit="sample")
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
            if pbar.n:
                pbar.set_postfix(acc=f"{correct / pbar.n:.2%}")
        except Exception:
            continue
    return correct


def evaluate_model(model_path, task_trained_on, num_test_samples=100,
                   results_file="experiments/ablation_results.csv"):
    print(f"Loading model from {model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, device_map="auto", dtype=torch.bfloat16
    )
    model.eval()

    results = {}
    samples_per_level = num_test_samples // len(LEVELS)

    # ── Standard tasks (CodeRunnability, CodeExecution, CodeInputDeduction) ──
    for eval_task_name, task_cls in TASKS_STANDARD.items():
        print(f"\n── {eval_task_name} ──")
        all_problems = []
        last_task_instance = None

        for level in LEVELS:
            task_instance = task_cls()
            task_instance.config.set_level(level)
            last_task_instance = task_instance
            try:
                problems = task_instance.generate_balanced_batch(batch_size=samples_per_level)
                all_problems.extend(problems)
                print(f"  Level {level}: {len(problems)} problems generated")
            except Exception as e:
                print(f"  Level {level}: generation failed — {e}")

        if not all_problems:
            results[eval_task_name] = 0.0
            continue

        correct = score_generation(
            model, tokenizer, all_problems, last_task_instance,
            desc=f"Eval {eval_task_name}"
        )
        accuracy = correct / len(all_problems)
        results[eval_task_name] = accuracy
        print(f"  {eval_task_name}: {accuracy:.2%} ({len(all_problems)} samples)")

    # ── Consolidation (direct generate(), bypass template timeout) ──
    print(f"\n── Consolidation ──")
    all_consolidation = []
    consolidation_task = None

    for level in LEVELS:
        problems, task_instance = _generate_consolidation_problems(
            level, CONSOLIDATION_SAMPLES_PER_LEVEL
        )
        all_consolidation.extend(problems)
        consolidation_task = task_instance
        print(f"  Level {level}: {len(problems)} problems generated")

    if all_consolidation and consolidation_task:
        correct = score_generation(
            model, tokenizer, all_consolidation, consolidation_task,
            desc="Eval Consolidation"
        )
        accuracy = correct / len(all_consolidation)
        results["Consolidation"] = accuracy
        print(f"  Consolidation: {accuracy:.2%} ({len(all_consolidation)} samples)")
    else:
        results["Consolidation"] = 0.0
        print("  Consolidation: no problems generated")

    # ── Save results ──
    os.makedirs(
        os.path.dirname(results_file) if os.path.dirname(results_file) else ".",
        exist_ok=True
    )
    file_exists = os.path.isfile(results_file)
    with open(results_file, mode='a', newline='') as f:
        fieldnames = [
            'Trained_On_Task',
            'Eval_CodeRunnability',
            'Eval_CodeExecution',
            'Eval_CodeInputDeduction',
            'Eval_Consolidation',
            'Levels',
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
            'Levels': str(LEVELS),
        })
    print(f"\nResults appended to {results_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=str, required=True)
    parser.add_argument("--trained_task", type=str, required=True)
    parser.add_argument("--samples", type=int, default=100,
                        help="Total samples per standard task (split across difficulty levels)")
    parser.add_argument("--results_file", type=str,
                        default="experiments/ablation_results.csv")
    args = parser.parse_args()
    evaluate_model(args.model_dir, args.trained_task, args.samples, args.results_file)