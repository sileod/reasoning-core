import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_surface_invariance_r4.gauss_link_code_walk.gauss_link_code_walk import (
    GaussLinkCodeWalk,
)

random.seed(382564971)

OUT = Path(__file__).with_name("samples_P003v2.md")


def main():
    lines = []
    lines.append("# P003v2 samples — gauss_link_code_walk")
    lines.append("")
    for level, tag in ((0, "Level 0"), (2, "Level 2"), (5, "Level 5")):
        lines.append(f"## {tag}")
        lines.append("")
        task = GaussLinkCodeWalk()
        for _ in range(2):
            ex = task.generate_example(level=level)
            lines.append("Prompt:")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    (OUT).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
