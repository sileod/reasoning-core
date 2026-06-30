import argparse
import json
import os
import sys

# Ensure reasoning_core is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reasoning_core.tasks.code_execution import (
    CodeRunnability,
    CodeExecution,
    CodeInputDeduction,
    Consolidation
)

TASKS = {
    "CodeRunnability": CodeRunnability,
    "CodeExecution": CodeExecution,
    "CodeInputDeduction": CodeInputDeduction,
    "Consolidation": Consolidation
}

def generate_data(task_name, num_samples, output_file):
    print(f"Generating {num_samples} samples for {task_name}...")
    task_cls = TASKS[task_name]
    task_instance = task_cls()
    
    dataset = []
    attempts = 0
    while len(dataset) < num_samples and attempts < num_samples * 10:
        attempts += 1
        try:
            problem = task_instance.generate()
            prompt = task_instance.prompt(problem.metadata)
            
            dataset.append({
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": str(problem.answer)}
                ],
                "task": task_name
            })
            if len(dataset) % 500 == 0:
                print(f"  Generated {len(dataset)}/{num_samples}")
        except Exception as e:
            continue
            
    with open(output_file, "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic code execution data")
    parser.add_argument("--task", type=str, choices=list(TASKS.keys()) + ["all"], required=True)
    parser.add_argument("--samples", type=int, default=10000, help="Total samples to generate")
    parser.add_argument("--out", type=str, required=True, help="Output JSONL file path")
    
    args = parser.parse_args()
    
    if args.task == "all":
        # Generate an equal mix for all 4 tasks
        samples_per_task = args.samples // len(TASKS)
        all_data = []
        for name in TASKS.keys():
            temp_out = f"temp_{name}.jsonl"
            generate_data(name, samples_per_task, temp_out)
            # Read back and append
            with open(temp_out, "r") as f:
                all_data.extend([json.loads(line) for line in f])
            os.remove(temp_out)
        
        with open(args.out, "w") as f:
            for item in all_data:
                f.write(json.dumps(item) + "\n")
        print(f"Saved {len(all_data)} mixed samples to {args.out}")
        
    else:
        generate_data(args.task, args.samples, args.out)
