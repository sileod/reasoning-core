"""Versioned evaluators shared by isolated pipeline parity experiments."""

import hashlib
import json
import os
from pathlib import Path

import torch


def load_qa_jsonl(path, eos_token, limit=None):
    path = Path(path).expanduser()
    rows = []
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("prompt") and row.get("answer") is not None:
                rows.append((f"{row['prompt']}\n", f"{row['answer']}{eos_token}"))
                if limit and len(rows) >= limit:
                    break
    return rows


@torch.no_grad()
def evaluate_qa_nll(model, tokenizer, examples, max_length):
    """Match per_task_influence.py eval_qa tokenization and aggregation exactly."""
    was_training = model.training
    model.eval()
    total_loss = total_tokens = 0
    per_example = []
    device = next(model.parameters()).device
    for prompt, answer in examples:
        prompt_ids = tokenizer(prompt, add_special_tokens=False).input_ids
        answer_ids = tokenizer(answer, add_special_tokens=False).input_ids
        if len(prompt_ids) + len(answer_ids) > max_length:
            per_example.append(None)
            continue
        input_ids = torch.tensor([prompt_ids + answer_ids], device=device)
        labels = input_ids.clone()
        labels[0, :len(prompt_ids)] = -100
        loss = model(input_ids, labels=labels).loss.item()
        tokens = (labels[0, 1:] != -100).sum().item()
        total_loss += loss * tokens
        total_tokens += tokens
        per_example.append(loss)
    model.train(was_training)
    return {
        "nll": total_loss / max(total_tokens, 1),
        "tokens": total_tokens,
        "examples": len(examples),
        "scored_examples": sum(value is not None for value in per_example),
        "per_example": per_example,
    }


def eval_id(name, path, limit=None):
    content = Path(path).expanduser().read_bytes()
    digest = hashlib.sha256(content + f"\0limit={limit}".encode()).hexdigest()[:12]
    return f"{name}/answer_nll@v1:{digest}"


def save_eval(run_dir, identifier, result):
    path = Path(run_dir) / "evals" / f"{safe_name(identifier)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"eval_id": identifier, **result}, indent=2) + "\n")
    os.replace(tmp, path)
    return path


def load_eval(run_dir, identifier):
    path = Path(run_dir) / "evals" / f"{safe_name(identifier)}.json"
    return json.loads(path.read_text())


def safe_name(value):
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)
