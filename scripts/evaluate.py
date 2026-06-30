import argparse
import json
import os
import csv
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
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

def evaluate_model(model_path, task_trained_on, num_test_samples=100, results_file="experiments/ablation_results.csv"):
    print(f"Loading model from {model_path} for evaluation...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.bfloat16)
    model.eval()
    
    results = {}
    
    # We evaluate the model on ALL tasks to see cross-task generalization
    for eval_task_name, task_cls in TASKS.items():
        print(f"Evaluating on {eval_task_name}...")
        task_instance = task_cls()
        
        correct = 0
        total = 0
        
        while total < num_test_samples:
            try:
                problem = task_instance.generate()
                prompt = task_instance.prompt(problem.metadata)
                
                # Format as ChatML
                chat = [{"role": "user", "content": prompt}]
                prompt_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
                
                inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)
                
                with torch.no_grad():
                    outputs = model.generate(
                        **inputs, 
                        max_new_tokens=128, 
                        temperature=0.0, # Greedy decoding for exact metrics
                        do_sample=False,
                        pad_token_id=tokenizer.eos_token_id
                    )
                
                # Extract only the newly generated text
                gen_text = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
                
                # Score the answer using the built-in logic
                score = task_instance.score_answer(gen_text, problem)
                correct += score
                total += 1
                
            except Exception as e:
                # Generation might fail occasionally due to constraints
                continue
                
        accuracy = correct / total
        results[eval_task_name] = accuracy
        print(f"  Accuracy on {eval_task_name}: {accuracy:.2%}")

    # Save to CSV for the paper
    file_exists = os.path.isfile(results_file)
    with open(results_file, mode='a', newline='') as f:
        fieldnames = ['Trained_On_Task', 'Eval_CodeRunnability', 'Eval_CodeExecution', 'Eval_CodeInputDeduction', 'Eval_Consolidation']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        row = {
            'Trained_On_Task': task_trained_on,
            'Eval_CodeRunnability': results.get('CodeRunnability', 0.0),
            'Eval_CodeExecution': results.get('CodeExecution', 0.0),
            'Eval_CodeInputDeduction': results.get('CodeInputDeduction', 0.0),
            'Eval_Consolidation': results.get('Consolidation', 0.0),
        }
        writer.writerow(row)
    print(f"Results appended to {results_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", type=str, required=True)
    parser.add_argument("--trained_task", type=str, required=True)
    parser.add_argument("--samples", type=int, default=100)
    args = parser.parse_args()
    
    evaluate_model(args.model_dir, args.trained_task, args.samples)
