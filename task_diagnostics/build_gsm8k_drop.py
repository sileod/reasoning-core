#!/usr/bin/env python3
"""Build GSM8K + DROP held-out transfer eval sets (short-answer, matches our answer-only legs).

  * gsm8k_eval.jsonl : prompt="<question>\nAnswer:", answer=<final number after '####'>  (MATH)
  * drop_eval.jsonl  : prompt="<passage>\n<question>\nAnswer:", answer=<gold span/number> (NUM/READING)
Each leg is scored two ways downstream: teacher-forced answer-NLL (gsm8k_nll/drop_nll) AND free-gen
exact-match (gsm8k_em/drop_em, numeric-aware). git-tracked builder; data_cache is per-machine, so run
once per machine: `python task_diagnostics/build_gsm8k_drop.py`.
"""
import json, re
from pathlib import Path
from datasets import load_dataset

DC = Path(__file__).resolve().parent.parent / "data_cache"
DC.mkdir(parents=True, exist_ok=True)
CAP = 300

# ── GSM8K ──────────────────────────────────────────────────────────────────────
g = load_dataset("openai/gsm8k", "main", split="test")
rows = []
for r in g:
    q = str(r["question"]).strip()
    sol = str(r["answer"])
    m = re.search(r"####\s*(.+)", sol)
    if not m: continue
    ans = m.group(1).strip().replace(",", "")
    if not re.search(r"-?\d", ans): continue
    rows.append({"prompt": f"{q}\nAnswer:", "answer": ans})
    if len(rows) >= CAP: break
(DC / "gsm8k_eval.jsonl").write_text("\n".join(map(json.dumps, rows)) + "\n")
print(f"gsm8k: n={len(rows)}")

# ── DROP ───────────────────────────────────────────────────────────────────────
d = load_dataset("ucinlp/drop", split="validation")
rows, seen = [], set()
for r in d:
    sp = (r.get("answers_spans") or {}).get("spans") or []
    ans = str(sp[0]).strip() if sp else ""
    if not ans: continue
    q = str(r["question"]).strip(); psg = str(r["passage"]).strip()
    key = (psg[:80], q)
    if key in seen: continue           # DROP repeats a passage across its sub-questions
    seen.add(key)
    rows.append({"prompt": f"{psg}\n{q}\nAnswer:", "answer": ans})
    if len(rows) >= CAP: break
(DC / "drop_eval.jsonl").write_text("\n".join(map(json.dumps, rows)) + "\n")
print(f"drop:  n={len(rows)}")
