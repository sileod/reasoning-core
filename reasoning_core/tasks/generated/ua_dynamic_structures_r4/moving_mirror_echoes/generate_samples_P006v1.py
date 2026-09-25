import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dynamic_structures_r4.moving_mirror_echoes.moving_mirror_echoes import (
    MovingMirrorEchoes,
)

SEED = 798610012

OUT = Path(__file__).with_name("samples_P006v1.md")


def main():
    lines = ["# Samples P006v1: moving_mirror_echoes", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            random.seed(SEED + level * 1000 + i)
            task = MovingMirrorEchoes()
            task.config.set_level(level)
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append("### Prompt")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("### Answer")
            lines.append("```")
            lines.append(x.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(OUT)


if __name__ == "__main__":
    main()
