import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_language_implementation_r4.attentional_blink_gating.attentional_blink_gating import (
    AttentionalBlinkGating,
)

random.seed(3536382515)


def main():
    out = Path(__file__).with_name("samples_P004v1.md")
    lines = []
    task = AttentionalBlinkGating()
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
