import random
from pathlib import Path

from reasoning_core.template import Task

from suspended_affix_reconstruction import SuspendedAffixReconstruction

SEED = 3536382515

OUT = Path(__file__).with_name("samples_P004v1.md")


def main():
    random.seed(SEED)
    task = SuspendedAffixReconstruction()
    lines = []
    lines.append("# Samples: suspended_affix_reconstruction")
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append(f"### Example")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append(f"**Answer**: `{x.answer}`")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
