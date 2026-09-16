"""Generate samples_P002v2.md for the tree_transducer_run trial.

Seeded via the module global RNG with a fixed seed so output is byte-reproducible.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r1.tree_transducer_run.tree_transducer_run import (
    TreeTransducerRun,
)

SEED = 1336314872
OUT = Path(__file__).with_name("samples_P002v2.md")

LEVELS = [0, 2, 5]
PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = TreeTransducerRun()
    lines = ["# Samples for tree_transducer_run (P002v2)", ""]
    for level in LEVELS:
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(PER_LEVEL):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"`{entry.answer}`")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
