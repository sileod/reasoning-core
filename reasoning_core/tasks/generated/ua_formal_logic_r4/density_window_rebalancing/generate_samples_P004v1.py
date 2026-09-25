import random
from pathlib import Path

from reasoning_core.template import Task

from density_window_rebalancing import DensityWindowRebalancing

SEED = 3536382515
OUT = Path(__file__).with_name("samples_P004v1.md")


def main():
    random.seed(SEED)
    task = DensityWindowRebalancing()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append("### Prompt")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
