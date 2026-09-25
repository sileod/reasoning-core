"""Generate samples_P007v3.md for the frame_independent_observables trial."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_invariants_r4.frame_independent_observables.frame_independent_observables import (
    FrameIndependentObservables,
)

SEED = 1034322864
OUT = Path(__file__).with_name("samples_P007v3.md")


def main():
    random.seed(SEED)
    task = FrameIndependentObservables()
    lines = []
    sample_idx = 0
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            sample_idx += 1
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append(f"### Example {sample_idx}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:** " + ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
