import random
import importlib.util
import os
from pathlib import Path

random.seed(1475571465)

HERE = Path(__file__).with_name("cyclic_trace_invariants.py")
spec = importlib.util.spec_from_file_location("cyclic_trace_invariants", HERE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CyclicTraceInvariants = mod.CyclicTraceInvariants

OUT = Path(__file__).with_name("samples_P002v1.md")

lines = []
lines.append("# samples P002v1: cyclic_trace_invariants")
lines.append("")
lines.append("Each instance gives two matrix words over noncommuting real square matrices and asks")
lines.append("whether their traces are equal. '^T' transposes a factor, '^X' marks a skew-symmetric")
lines.append("factor M = -M^T. Use trace(MN) = trace(NM) (cyclicity) and trace(M) = trace(M^T).")
lines.append("")

task = CyclicTraceInvariants()

for level in (0, 2, 5):
    cfg = task.config_cls()
    cfg.set_level(level)
    task.config = cfg
    lines.append(f"## Level {level}")
    lines.append("")
    for i in range(2):
        entry = task.generate_entry()
        prompt = task.render_prompt(entry.metadata)
        lines.append(f"### Example {i + 1}")
        lines.append("Prompt:")
        lines.append("```")
        lines.append(prompt)
        lines.append("```")
        lines.append(f"Answer: {entry.answer}")
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
