import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from reasoning_core.tasks.generated.ua_compositional_generalization_r5.composed_lens_update.composed_lens_update import (  # noqa: E402
    ComposedLensUpdate,
)

SEED = 1336314872
out = Path(__file__).resolve().with_name("samples_P002v2.md")

lines = []
lines.append("# samples_P002v2 — composed lens update v2")
lines.append("")


def emit(task, level, n):
    task.config.set_level(level)
    examples = [task.generate_example() for _ in range(n)]
    lines.append(f"## Level {level}")
    lines.append("")
    for idx, ex in enumerate(examples, 1):
        lines.append(f"### Example {idx}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(task.render_prompt(ex.metadata))
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(ex.answer)
        lines.append("")
    lines.append("")


random.seed(SEED)
task = ComposedLensUpdate()
emit(task, 0, 2)
emit(task, 2, 2)
emit(task, 5, 2)

out.write_text("\n".join(lines))
print(out)
