import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_transfer_r4.quadratic_refinement_arf_recovery.quadratic_refinement_arf_recovery import (
    QuadraticRefinementArfRecovery,
)

SEED = 2072234021
OUT = Path(__file__).with_name("samples_P005v2.md")


def render_level(task, level):
    task.config.set_level(level)
    chunks = []
    for i in range(2):
        entry = task.generate_example()
        chunks.append(f"### Example {i + 1}\n")
        chunks.append(f"**Prompt:** {entry.metadata['_prompt'] if '_prompt' in entry.metadata else task.render_prompt(entry.metadata)}\n")
        chunks.append(f"**Answer:** {entry.answer}\n")
    return "\n".join(chunks)


def main():
    random.seed(SEED)
    task = QuadraticRefinementArfRecovery()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        lines.append(render_level(task, level))
        lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
