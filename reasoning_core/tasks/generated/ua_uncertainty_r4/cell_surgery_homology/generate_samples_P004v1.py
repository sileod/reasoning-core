import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.cell_surgery_homology.cell_surgery_homology import (
    CellSurgeryHomology,
)

SEED = 3536382515
OUT = Path(__file__).with_name("samples_P004v1.md")


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            t = CellSurgeryHomology()
            e = t.generate_example(level=level)
            prompt = t.render_prompt(e.metadata)
            lines.append(f"### Example")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
