import os
import random

seed = 382564971
random.seed(seed)

from reasoning_core.tasks.generated.k3_invariants_r1.stack_sorting_discipline.stack_sorting_discipline import (  # noqa: E402
    StackSortingDiscipline, StackSortingConfig)


def emit(level):
    cfg = StackSortingConfig()
    cfg.set_level(level)
    task = StackSortingDiscipline()
    task.config = cfg
    lines = [f"### Level {level}"]
    for _ in range(2):
        x = task.generate_example()
        lines.append("\nPrompt:")
        lines.append(task.render_prompt(x.metadata))
        lines.append("\nAnswer:")
        lines.append(x.answer)
    return "\n".join(lines)


parts = []
for lvl in (0, 2, 5):
    parts.append(emit(lvl))

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "samples_P003v2.md"), "w") as f:
    f.write("\n".join(parts) + "\n")
