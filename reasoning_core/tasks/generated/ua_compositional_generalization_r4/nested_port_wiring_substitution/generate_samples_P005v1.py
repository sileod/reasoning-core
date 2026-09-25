"""Generate samples_P005v1.md for levels 0, 2 and 5."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.nested_port_wiring_substitution.nested_port_wiring_substitution import NestedPortWiringSubstitution

SEED = 729651269
random.seed(SEED)

out = Path(__file__).with_name("samples_P005v1.md")
task = NestedPortWiringSubstitution()

lines = ["# Samples for nested_port_wiring_substitution (P005v1)\n"]
for level in (0, 2, 5):
    lines.append(f"## Level {level}\n")
    task.config.set_level(level)
    for _ in range(2):
        x = task.generate_example()
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(x.render() if hasattr(x, "render") else task.render_prompt(x.metadata))
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(x.answer)
        lines.append("")
        lines.append("---")
        lines.append("")

out.write_text("\n".join(lines))
print("wrote", out)
