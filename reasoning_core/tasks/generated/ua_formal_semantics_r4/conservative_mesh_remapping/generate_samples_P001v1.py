import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_semantics_r4.conservative_mesh_remapping.conservative_mesh_remapping import (
    ConservativeMeshRemapping,
)

random.seed(1662004003)

OUT = Path(__file__).with_name("samples_P001v1.md")
task = ConservativeMeshRemapping()

with open(OUT, "w") as f:
    f.write("# Samples P001v1: conservative_mesh_remapping\n\n")
    for level in (0, 2, 5):
        task.config.set_level(level)
        f.write("## Level %d\n\n" % level)
        for _ in range(2):
            e = task.generate_example()
            f.write("**Prompt:**\n\n")
            f.write(task.render_prompt(e.metadata))
            f.write("\n\n**Answer:**\n\n")
            f.write(e.answer)
            f.write("\n\n---\n\n")
