import pathlib
import random

random.seed(729651269)

import importlib

mod = importlib.import_module(
    "reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.ellipsis_reconstruction.ellipsis_reconstruction"
)

task = mod.EllipsisReconstruction()

out = [f"# samples_P005v1", ""]

for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"## Level {level}")
    out.append("")
    for _ in range(2):
        x = task.generate_example()
        out.append(f"**Prompt:** {task.render_prompt(x.metadata)}")
        out.append("")
        out.append(f"**Answer:** {x.answer}")
        out.append("")

pathlib.Path(__file__).with_name("samples_P005v1.md").write_text("\n".join(out))
print("wrote samples_P005v1.md")
