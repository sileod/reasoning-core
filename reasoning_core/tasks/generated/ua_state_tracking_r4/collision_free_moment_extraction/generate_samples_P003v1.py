import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_state_tracking_r4.collision_free_moment_extraction.moment_extraction import (
    CollisionFreeMomentExtraction,
)

OUT = Path(__file__).with_name("samples_P003v1.md")


def main():
    random.seed(2267388306)
    task = CollisionFreeMomentExtraction()
    lines = ["# Samples for collision_free_moment_extraction (P003v1)", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("## Level %d" % level)
        lines.append("")
        for i in range(2):
            entry = task.generate_example()
            lines.append("### Example %d" % (i + 1))
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
