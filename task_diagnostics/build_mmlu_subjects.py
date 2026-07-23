#!/usr/bin/env python3
"""Build per-subject MMLU eval sets (BOTH cloze and normal/letter) for richer per-subject audit.

Splits the aggregate math/logic legs into their component MMLU subjects so transfer can be read PER SUBJECT
(and a broader math aggregate reconstructed) instead of leaning on high_school_math (270) only.
  * mmlu_<subj>_cloze_eval.jsonl : options OMITTED from prompt, answer = gold option TEXT  (format-fair NLL)
  * mmlu_<subj>_eval.jsonl       : options listed A./B./C./D. in prompt, answer = gold LETTER (standard MCQ)
Each leg gated EVAL_MMLU_<SUBJECT>[_CLOZE]=1. git-tracked; data_cache is per-machine, so run once per machine:
`python task_diagnostics/build_mmlu_subjects.py`.
"""
import json, string
from pathlib import Path
from datasets import load_dataset

SUBJECTS = ["abstract_algebra", "college_mathematics", "elementary_mathematics",
            "high_school_mathematics", "high_school_statistics", "formal_logic"]
DC = Path(__file__).resolve().parent.parent / "data_cache"
DC.mkdir(parents=True, exist_ok=True)

for subj in SUBJECTS:
    d = load_dataset("cais/mmlu", subj, split="test")
    cloze, normal = [], []
    for r in d:
        ch = [str(c).strip() for c in r["choices"]]
        gi = int(r["answer"])
        q = str(r["question"]).strip()
        if len(ch) < 2 or not (0 <= gi < len(ch)) or not ch[gi]:
            continue
        cloze.append({"prompt": f"{q}\nAnswer:", "answer": ch[gi], "choices": ch, "answer_idx": gi})
        menu = "\n".join(f"{string.ascii_uppercase[i]}. {c}" for i, c in enumerate(ch))
        normal.append({"prompt": f"{q}\n{menu}\nAnswer:", "answer": string.ascii_uppercase[gi]})
    (DC / f"mmlu_{subj}_cloze_eval.jsonl").write_text("\n".join(map(json.dumps, cloze)) + "\n")
    (DC / f"mmlu_{subj}_eval.jsonl").write_text("\n".join(map(json.dumps, normal)) + "\n")
    print(f"{subj}: cloze n={len(cloze)}  normal n={len(normal)}")
