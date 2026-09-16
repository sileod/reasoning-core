import importlib.util
import random
from pathlib import Path

_MOD_PATH = Path(__file__).with_name("case_government_assignment.py")
_spec = importlib.util.spec_from_file_location("case_government_assignment", _MOD_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

random.seed(525660630)
task = _mod.CaseGovernmentAssignment()
out = Path(__file__).with_name("samples_P011v2.md")
lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    for i in range(2):
        ex = task.generate_example(level=level)
        lines.append(f"### Example {i + 1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(ex.prompt)
        lines.append("")
        lines.append(f"**Answer:** {ex.answer}")
        lines.append("")
out.write_text("\n".join(lines))
