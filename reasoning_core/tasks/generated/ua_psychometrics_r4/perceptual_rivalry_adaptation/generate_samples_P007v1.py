import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_psychometrics_r4.perceptual_rivalry_adaptation.perceptual_rivalry_adaptation import (
    PerceptualRivalryAdaptation,
)


def main():
    random.seed(1139467751)
    task = PerceptualRivalryAdaptation()
    lines = ["# Perceptual Rivalry Adaptation (P007v1) samples", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    out = Path(__file__).with_name("samples_P007v1.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
