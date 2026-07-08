import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED

from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from reasoning_core.tasks.code_execution import (
    CodeRunnability,
    CodeExecution,
    CodeInputDeduction,
    Consolidation,
    ConsolidationConfig,
)

TASKS = {
    "CodeRunnability": CodeRunnability,
    "CodeExecution": CodeExecution,
    "CodeInputDeduction": CodeInputDeduction,
    "Consolidation": Consolidation,
}

# Normalize class names to task_name strings used in run_sft.py's --aux_task filter
# (must match _value(row, "task") in controlled_experiment.py)
TASK_NAME_MAP = {
    "CodeRunnability": "code_runnability",
    "CodeExecution": "code_execution",
    "CodeInputDeduction": "code_input_deduction",
    "Consolidation": "code_consolidation",
}

# 80% of samples at level 0, 10% at level 1, 10% at level 2.
# Supervisor said this is the right balance for a NeurIPS-level ablation:
# majority of training signal is easy/medium (level 0), with a tail of
# harder examples to avoid ceiling effects.
LEVEL_WEIGHTS = {0: 0.80, 1: 0.10, 2: 0.10}


def _make_task(task_name, level=0):
    if task_name == "Consolidation":
        cfg = ConsolidationConfig(timeout=1.0, max_attempts=300, n_programs=3)
        task = Consolidation(config=cfg)
    else:
        task = TASKS[task_name]()
    task.config.set_level(level)
    return task


def _generate_one_sample(args):
    """Top-level worker — must be picklable."""
    task_name, level = args
    try:
        task_instance = _make_task(task_name, level)
        problem = task_instance.generate()
        prompt = task_instance.prompt(problem.metadata)
        return {
            # prompt/answer format matches run_sft.py's get_formatter("rc") expectation
            "prompt": prompt,
            "answer": str(problem.answer),
            "task": TASK_NAME_MAP.get(task_name, task_name.lower()),
            "level": str(level),
            # also keep messages format for evaluate.py compatibility
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": str(problem.answer)},
            ],
        }
    except Exception:
        return None


def generate_data(task_name, num_samples, output_file, workers=None):
    if workers is None:
        workers = 2 if task_name == "Consolidation" else min(4, os.cpu_count() or 4)

    # Compute per-level sample counts from weights (ensure they sum to num_samples)
    level_counts = {}
    remaining = num_samples
    levels = sorted(LEVEL_WEIGHTS.keys())
    for i, level in enumerate(levels):
        if i == len(levels) - 1:
            level_counts[level] = remaining
        else:
            count = int(num_samples * LEVEL_WEIGHTS[level])
            level_counts[level] = count
            remaining -= count

    print(f"Generating {num_samples} samples for {task_name} "
          f"({workers} workers): " +
          ", ".join(f"level {l}={c}" for l, c in level_counts.items()))

    dataset = []

    for level, needed in level_counts.items():
        collected = 0
        max_attempts = needed * 15
        submitted = 0
        pbar = tqdm(total=needed, desc=f"{task_name} level={level}", unit="sample")

        with ProcessPoolExecutor(max_workers=workers) as executor:
            pending = set()
            max_pending = workers * 3

            def submit_more():
                nonlocal submitted
                while len(pending) < max_pending and submitted < max_attempts:
                    pending.add(executor.submit(_generate_one_sample, (task_name, level)))
                    submitted += 1

            submit_more()

            while pending and collected < needed:
                done, _ = wait(pending, return_when=FIRST_COMPLETED)
                for future in done:
                    pending.discard(future)
                    if collected >= needed:
                        continue
                    try:
                        result = future.result()
                        if result is not None:
                            dataset.append(result)
                            collected += 1
                            pbar.update(1)
                            pbar.set_postfix(submitted=submitted)
                    except Exception:
                        pass
                submit_more()

        pbar.close()

    with open(output_file, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
    print(f"Saved {len(dataset)} samples to {output_file} "
          f"(task names: {set(TASK_NAME_MAP.values())})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, choices=list(TASKS.keys()) + ["all"], required=True)
    parser.add_argument("--samples", type=int, default=10000,
                        help="Total samples — split 80/10/10 across difficulty levels 0/1/2")
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    if args.task == "all":
        samples_per_task = args.samples // len(TASKS)
        all_data = []
        for name in tqdm(TASKS.keys(), desc="Tasks", unit="task"):
            temp_out = f"temp_{name}.jsonl"
            generate_data(name, samples_per_task, temp_out, workers=args.workers)
            with open(temp_out, "r") as f:
                all_data.extend([json.loads(line) for line in f])
            os.remove(temp_out)
        with open(args.out, "w") as f:
            for item in all_data:
                f.write(json.dumps(item) + "\n")
        print(f"Saved {len(all_data)} mixed samples to {args.out}")
    else:
        generate_data(args.task, args.samples, args.out, workers=args.workers)