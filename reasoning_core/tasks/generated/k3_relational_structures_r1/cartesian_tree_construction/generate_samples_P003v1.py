import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relational_structures_r1.cartesian_tree_construction.cartesian_tree_construction import CartesianTreeConstruction  # noqa: E402

random.seed(2267388306)

task = CartesianTreeConstruction()

out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"# Level {level}")
    out.append("")
    for k in range(2):
        ex = task.generate_example()
        out.append(f"## Example {k+1}")
        out.append("")
        out.append(f"**Prompt:** {task.render_prompt(ex.metadata)}")
        out.append("")
        out.append(f"**Answer:** {ex.answer}")
        out.append("")

Path(__file__).with_name("samples_P003v1.md").write_text("\n".join(out))
