import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.cyk_chart_membership.cyk_chart_membership import CykChartMembership

random.seed(4238614268)

out = Path(__file__).with_name("samples_P001v3.md")
task = CykChartMembership()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task.config.set_level(level)
    lines.append("")
    n_examples = 2
    for k in range(n_examples):
        x = task.generate_example()
        lines.append(f"### Example {k + 1}")
        lines.append("")
        lines.append("Prompt:")
        lines.append("```")
        lines.append(task.render_prompt(x.metadata))
        lines.append("```")
        lines.append("")
        lines.append("Answer:")
        lines.append("```")
        lines.append(x.answer)
        lines.append("```")
        lines.append("")

out.write_text("\n".join(lines))
print(f"wrote {out}")
