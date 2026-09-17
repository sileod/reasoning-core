import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.compound_cue_weight_updates.compound_cue_weight_updates import (
    CompoundCueWeightUpdates,
)


def main():
    random.seed(3020341981)
    out = Path(__file__).with_name("samples_P008v2.md")
    lines = ["# Samples: compound_cue_weight_updates", ""]
    for level in (0, 2, 5):
        task = CompoundCueWeightUpdates()
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            entry = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(entry.prompt)
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
