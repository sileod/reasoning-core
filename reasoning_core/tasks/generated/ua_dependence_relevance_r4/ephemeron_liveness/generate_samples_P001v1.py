"""Generate samples_P001v1.md with two prompt/answer examples at levels 0, 2 and 5."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.ephemeron_liveness.ephemeron_liveness import (
    EphemeronLiveness,
)

seed = 1662004003
random.seed(seed)

LEVELS = (0, 2, 5)
PER_LEVEL = 2

out = Path(__file__).with_name("samples_P001v1.md")

lines = []
for level in LEVELS:
    t = EphemeronLiveness()
    t.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for _ in range(PER_LEVEL):
        ex = t.generate_example()
        lines.append(ex.prompt)
        lines.append("")
        lines.append("**Answer:** " + ex.answer)
        lines.append("")

out.write_text("\n".join(lines))
