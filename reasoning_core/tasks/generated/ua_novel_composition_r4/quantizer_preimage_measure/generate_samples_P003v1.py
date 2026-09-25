import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_novel_composition_r4.quantizer_preimage_measure.quantizer_preimage_measure import (
    QuantizerPreimageMeasure,
    QuantizerPreimageMeasureConfig,
)

SEED = 2267388306

OUT = Path(__file__).with_name("samples_P003v1.md")


def main():
    random.seed(SEED)
    task = QuantizerPreimageMeasure()
    lines = []
    lines.append("# samples_P003v1")
    lines.append("")
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for idx in range(2):
            cfg = QuantizerPreimageMeasureConfig()
            cfg.set_level(level)
            task.config = cfg
            ex = task.generate_example()
            lines.append(f"### Example {idx + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append(f"**Answer:** {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
