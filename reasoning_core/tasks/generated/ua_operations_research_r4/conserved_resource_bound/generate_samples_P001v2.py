"""Generate samples_P001v2.md for conserved_resource_bound trial."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

random.seed(2302342651)

from conserved_resource_bound_model import ConservedResourceBound  # noqa: E402


def main():
    out_path = Path(__file__).with_name("samples_P001v2.md")
    task = ConservedResourceBound()
    lines = []

    for level, label in ((0, "Level 0"), (2, "Level 2"), (5, "Level 5")):
        lines.append(f"## {label}")
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            x = task.generate_example()
            lines.append("### Prompt")
            lines.append("")
            lines.append(x.prompt)
            lines.append("")
            lines.append(f"### Answer")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
            lines.append("---")
            lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
