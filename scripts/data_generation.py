import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

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


def _make_task(task_name):
    """Instantiate a task, using tighter config for Consolidation during bulk generation."""
    if task_name == "Consolidation":
        cfg = ConsolidationConfig(
            timeout=1.0,       # was 3.0 — cuts per-attempt waste by 3x
            max_attempts=300,  # was 1000 — fail faster when nothing generates
            n_programs=3,
        )
        return Consolidation(config=cfg)
    return TASKS[task_name]()


def _generate_one_sample(task_name):
    """Top-level worker function (must be picklable — no lambdas or closures)."""
    try:
        task_instance = _make_task(task_name)
        problem = task_instance.generate()
        prompt = task_instance.prompt(problem.metadata)
        return {
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": str(problem.answer)},
            ],
            "task": task_name,
        }
    except Exception:
        return None


def generate_data(task_name, num_samples, output_file, workers=None):
    if workers is None:
        # Conservative default: Consolidation already forks internally,
        # so 2 outer workers = up to ~8 subprocesses at once on the laptop.
        # Other tasks are lighter so we give them more workers.
        workers = 2 if task_name == "Consolidation" else min(4, os.cpu_count() or 4)

    print(f"Generating {num_samples} samples for {task_name} ({workers} workers)...")
    dataset = []
    max_attempts = num_samples * 15
    attempts_submitted = 0
    pbar = tqdm(total=num_samples, desc=task_name, unit="sample")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # Keep a rolling window of futures so workers stay busy
        pending = set()
        max_pending = workers * 3

        def _submit_more():
            nonlocal attempts_submitted
            while len(pending) < max_pending and attempts_submitted < max_attempts:
                pending.add(executor.submit(_generate_one_sample, task_name))
                attempts_submitted += 1

        _submit_more()

        while pending and len(dataset) < num_samples:
            # Wait for at least one future to finish
            from concurrent.futures import wait, FIRST_COMPLETED
            done, _ = wait(pending, return_when=FIRST_COMPLETED)

            for future in done:
                pending.discard(future)
                if len(dataset) >= num_samples:
                    continue
                try:
                    result = future.result()
                    if result is not None:
                        dataset.append(result)
                        pbar.update(1)
                        pbar.set_postfix(submitted=attempts_submitted, workers=workers)
                except Exception:
                    pass

            _submit_more()

    pbar.close()

    with open(output_file, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
    print(f"Saved {len(dataset)} samples to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic code execution data")
    parser.add_argument("--task", type=str, choices=list(TASKS.keys()) + ["all"], required=True)
    parser.add_argument("--samples", type=int, default=10000)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--workers", type=int, default=None,
                        help="Parallel workers. Default: 2 for Consolidation, 4 for others.")
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