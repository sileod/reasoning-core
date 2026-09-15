import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_rule_induction_r1.tuple_generating_dependency_chase.tuple_generating_dependency_chase import (
    TupleGeneratingDependencyChase,
)

random.seed(1662004003)

task = TupleGeneratingDependencyChase()

out = []
for level in (0, 2, 5):
    out.append(f"# Level {level}")
    out.append("")
    task.config.set_level(level)
    for i in range(2):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        out.append(f"## Example {i + 1}")
        out.append("")
        out.append("**Prompt:**")
        out.append("")
        out.append("```")
        out.append(prompt)
        out.append("```")
        out.append("")
        out.append("**Answer:**")
        out.append("")
        out.append("```")
        out.append(entry.answer)
        out.append("```")
        out.append("")
    out.append("")

Path(__file__).with_name("samples_P001v1.md").write_text("\n".join(out), encoding="utf-8")
print("wrote samples_P001v1.md")
