"""Write two prompt/answer examples at levels 0, 2 and 5 for P010v2.

Seeded so the file is byte-reproducible across processes and hash seeds.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r4.pivot_rotation_fixture_building.pivot_rotation_fixture_building import (
    PivotRotationFixtureBuilding,
)


def main():
    random.seed(1211525277)
    task = PivotRotationFixtureBuilding()
    out_dir = Path(__file__).with_name("samples_P010v2.md")
    lines = [
        "# P010v2 pivot_rotation_fixture_building samples",
        "",
    ]
    for level in (0, 2, 5):
        lines.append("# Level %d" % level)
        lines.append("")
        task.config.set_level(level)
        for which in (1, 2):
            entry = task.generate_example()
            lines.append("## Example %d" % which)
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    out_dir.write_text("\n".join(lines) + "\n")
    print("wrote", out_dir)


if __name__ == "__main__":
    main()
