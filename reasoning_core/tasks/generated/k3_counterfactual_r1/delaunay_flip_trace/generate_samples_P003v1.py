import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

import random

random.seed(2267388306)

from reasoning_core.tasks.generated.k3_counterfactual_r1.delaunay_flip_trace.delaunay_flip_trace import DelaunayFlipTrace


def main():
    task = DelaunayFlipTrace()
    out = Path(__file__).with_name("samples_P003v1.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append("**Prompt:**")
            lines.append(prompt)
            lines.append("")
            lines.append(f"**Answer:** {entry.answer}")
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
