import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_semantics_r4.negative_concord_interpretation.negative_concord_interpretation import (
    NegativeConcordInterpretation,
)

random.seed(3713447331)

task = NegativeConcordInterpretation()
out = Path(__file__).with_name("samples_P009v3.md")

lines = []
lines.append("# Samples P009v3")
lines.append("")

for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    task.config.set_level(level)
    for i in range(2):
        e = task.generate_example()
        prompt = task.render_prompt(e.metadata)
        lines.append(f"### Example {i+1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append("```")
        lines.append(prompt)
        lines.append("```")
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(f"`{e.answer}`")
        lines.append("")

out.write_text("\n".join(lines))
print("wrote", out)
