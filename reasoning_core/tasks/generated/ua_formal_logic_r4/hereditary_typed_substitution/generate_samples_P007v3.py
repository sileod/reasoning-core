import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r4.hereditary_typed_substitution.hereditary_typed_substitution import (
    HereditaryTypedSubstitution,
)

random.seed(1034322864)

out = Path(__file__).with_name("samples_P007v3.md")
lines = ["# Samples P007v3\n"]
for level in (0, 2, 5):
    lines.append(f"## Level {level}\n")
    task = HereditaryTypedSubstitution()
    task.config.set_level(level)
    for i in range(2):
        e = task.generate_example()
        lines.append(f"### Example {i+1}\n")
        lines.append("**Prompt:**\n")
        lines.append(f"{task.render_prompt(e.metadata)}\n")
        lines.append("**Answer:**\n")
        lines.append(f"{e.answer}\n")
    lines.append("")

out.write_text("\n".join(lines))
print(f"wrote {out}")
