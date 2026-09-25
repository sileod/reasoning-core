import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_paraphrase_equivalence_r4.portmanteau_spellout.portmanteau_spellout import (
    PortmanteauSpellout,
)

random.seed(1662004003)

out_path = Path(__file__).with_name("samples_P001v1.md")
lines = ["# samples_P001v1", ""]
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    t = PortmanteauSpellout()
    t.config.set_level(level)
    for idx in range(1, 3):
        ex = t.generate_example()
        lines.append(f"### Example {idx}")
        lines.append("")
        lines.append(ex.prompt)
        lines.append("")
        lines.append(f"Answer: {ex.answer}")
        lines.append("")

with open(out_path, "w") as fh:
    fh.write("\n".join(lines))
print("wrote", out_path)
