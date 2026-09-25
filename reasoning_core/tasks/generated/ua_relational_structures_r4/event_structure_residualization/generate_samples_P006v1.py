"""Generate the required samples_P006v1.md for the event-structure residualization trial.

Seeded so the output is byte-reproducible under the recorded requested seed.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_relational_structures_r4.event_structure_residualization.event_structure_residualization import (
    EventStructureResidualization,
)

random.seed(798610012)

task = EventStructureResidualization()

out_path = Path(__file__).with_name("samples_P006v1.md")

chunks = ["# Event Structure Residualization — samples", ""]

for level in (0, 2, 5):
    task.config.set_level(level)
    chunks.append(f"# Level {level}")
    chunks.append("")
    for _ in range(2):
        ex = task.generate_example()
        chunks.append("**Prompt:**")
        chunks.append("```")
        chunks.append(ex.prompt)
        chunks.append("```")
        chunks.append("")
        chunks.append("**Answer:**")
        chunks.append("```")
        chunks.append(ex.answer)
        chunks.append("```")
        chunks.append("")

out_path.write_text("\n".join(chunks))
print("wrote", out_path)
