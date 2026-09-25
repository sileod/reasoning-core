import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.sequential_bet_calibration.sequential_bet_calibration import (
    SequentialBetCalibration,
)

random.seed(2302342651)

OUT = Path(__file__).with_name("samples_P001v2.md")


def main():
    t = SequentialBetCalibration()
    lines = []
    for level in (0, 2, 5):
        t.config.set_level(level)
        lines.append(f"## Level {level}")
        for i in range(2):
            e = t.generate_example()
            prompt = t.render_prompt(e.metadata)
            lines.append(f"### Example {i + 1}")
            lines.append("Prompt:")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {e.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(OUT)


if __name__ == "__main__":
    main()
