import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_invariants_r4.local_quantum_sufficiency.local_quantum_sufficiency import (
    LocalQuantumSufficiency,
)

random.seed(3536382515)
OUT = Path(__file__).with_name("samples_P004v1.md")


def render(level):
    t = LocalQuantumSufficiency()
    t.config.set_level(level)
    return [t.generate_example() for _ in range(2)]


lines = []
for level in (0, 2, 5):
    lines.append("## Level %d" % level)
    for i, ex in enumerate(render(level)):
        lines.append("### Example %d" % (i + 1))
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(ex.prompt)
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(ex.answer)
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
