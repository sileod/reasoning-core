"""Generate samples_P051v1.md for the minimal_unsat_core task."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.manual_high_value_80_r1.minimal_unsat_core.minimal_unsat_core import (  # noqa: E501
    MinimalUnsatCore,
)

SEED = 1787056888


def main():
    random.seed(SEED)
    task = MinimalUnsatCore()
    out = Path(__file__).with_name("samples_P051v1.md")
    lines = ["# minimal_unsat_core samples (P051v1)\n"]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("\n## Level %d\n" % level)
        for _ in range(2):
            ex = task.generate_example()
            lines.append("\n**Prompt:**\n")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("\n**Answer:**\n")
            lines.append(ex.answer)
            lines.append("\n")
    out.write_text("\n".join(lines))
    print(out.resolve())


if __name__ == "__main__":
    main()
