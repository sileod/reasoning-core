import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_logic_r4.cfg_ambiguity_witness import (
    cfg_ambiguity_witness as mod,
)

random.seed(1618848011)
out = Path(__file__).with_name("samples_P008v3.md")
lines = []
task = mod.CFGAmbiguityWitness()
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    count = 0
    while count < 2:
        e = task.generate_entry()
        lines.append("### Example")
        lines.append("")
        lines.append("Prompt:")
        lines.append("")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append("Answer:")
        lines.append("")
        lines.append(e.answer)
        lines.append("")
        count += 1
out.write_text("\n".join(lines), encoding="utf-8")
