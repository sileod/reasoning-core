import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.polarity_item_licensing.polarity_item_licensing import (
    PolarityItemLicensing,
)

random.seed(2267388306)

OUT = Path(__file__).with_name("samples_P003v1.md")


def main():
    task = PolarityItemLicensing()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for _ in range(2):
            e = task.generate_example()
            prompt = task.render_prompt(e.metadata)
            lines.append("**Prompt:**")
            lines.append(prompt)
            lines.append("")
            lines.append(f"**Answer:** {e.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
