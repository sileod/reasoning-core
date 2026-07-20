#!/usr/bin/env python3
"""Build <repo>/data_cache/folio_eval.jsonl — FOLIO (first-order-logic NL entailment) as a cloze leg.

git-tracked so any machine (local, G5K) can regenerate the eval without rsync: `python task_diagnostics/build_folio_eval.py`.
data_cache is untracked (symlink locally / real dir on G5K), so the DATA is rebuilt per machine; only this
builder travels via git. Cloze-fair format (answer TEXT scored, no options in the prompt) like mmlu_*_cloze;
`choices` enables length-normalised choice-scoring accuracy. Gate the leg with EVAL_FOLIO=1.
"""
import json
from collections import Counter
from pathlib import Path
from datasets import load_dataset

OUT = Path(__file__).resolve().parent.parent / "data_cache" / "folio_eval.jsonl"
CHOICES = ["True", "False", "Uncertain"]

d = load_dataset("yale-nlp/FOLIO")["validation"]
rows, seen = [], set()
for r in d:
    lab, prem, conc = str(r["label"]).strip(), str(r["premises"]).strip(), str(r["conclusion"]).strip()
    if lab not in CHOICES or not prem or not conc or (prem, conc) in seen:
        continue
    seen.add((prem, conc))
    prompt = (f"{prem}\n\nQuestion: Based on the premises above, is the following statement "
              f"true, false, or uncertain?\nStatement: {conc}\nAnswer:")
    rows.append({"prompt": prompt, "answer": lab, "choices": CHOICES, "answer_idx": CHOICES.index(lab)})

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(json.dumps(x) for x in rows) + "\n")
print(f"wrote {OUT}  n={len(rows)}  label_dist={dict(Counter(r['answer'] for r in rows))}")
