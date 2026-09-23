import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_global_from_local_r4.lindley_wait_propagation.lindley_wait_propagation import (
    LindleyWaitPropagation,
)

random.seed(1662004003)

task = LindleyWaitPropagation()

out_lines = []
for level in (0, 2, 5):
    out_lines.append(f"## Level {level}\n")
    task.config.set_level(level)
    for _ in range(2):
        e = task.generate_example()
        out_lines.append("**Prompt:**")
        out_lines.append(task.render_prompt(e.metadata))
        out_lines.append("")
        out_lines.append("**Answer:**")
        out_lines.append(e.answer)
        out_lines.append("")

out_path = Path(__file__).with_name("samples_P001v1.md")
out_path.write_text("\n".join(out_lines))
print(out_path)
