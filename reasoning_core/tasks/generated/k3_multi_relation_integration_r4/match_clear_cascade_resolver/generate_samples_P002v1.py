import random
from pathlib import Path

random.seed(1475571465)

from reasoning_core.tasks.generated.k3_multi_relation_integration_r4.match_clear_cascade_resolution.match_clear_cascade_resolution import (
    MatchClearCascadeResolver,
)

task = MatchClearCascadeResolver()
levels = [0, 2, 5]
per_level = 2

out = Path(__file__).with_name("samples_P002v1.md")
lines = ["# Samples for match_clear_cascade_resolution (P002v1)\n"]
for lvl in levels:
    task.config.set_level(lvl)
    lines.append(f"## Level {lvl}\n")
    for i in range(per_level):
        x = task.generate_example()
        lines.append(f"### Example {i + 1}\n")
        lines.append("Prompt:\n")
        lines.append(task.render_prompt(x.metadata) + "\n")
        lines.append("Answer:\n")
        lines.append(x.answer + "\n")
    lines.append("")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {out}")
