import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dynamic_structures_r4.epistemic_event_product_update.epistemic_event_product_update import (
    EpistemicEventProductUpdate,
)

random.seed(1336314872)

out = []
for level, label in ((0, "Level 0"), (2, "Level 2"), (5, "Level 5")):
    task = EpistemicEventProductUpdate()
    task.config.set_level(level)
    out.append(f"## {label}")
    for i in range(2):
        ex = task.generate_example()
        out.append(f"### Example {i + 1}")
        out.append("**Prompt:**")
        out.append(ex.prompt)
        out.append("**Answer:**")
        out.append(ex.answer)
        out.append("")

Path(__file__).with_name("samples_P002v2.md").write_text("\n".join(out) + "\n")
