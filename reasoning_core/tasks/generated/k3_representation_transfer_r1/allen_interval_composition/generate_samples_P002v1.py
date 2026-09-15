"""Generate the samples_P002v1.md file for the Allen interval composition task."""

import random
from pathlib import Path

import allen_interval_composition as task_module

random.seed(1475571465)

OUT = Path(__file__).with_name("samples_P002v1.md")


def main():
    levels = [0, 2, 5]
    lines = ["# Samples for P002v1 - allen_interval_composition", ""]
    for level in levels:
        config = task_module.AllenIntervalCompositionV1Config()
        config.set_level(level)
        task = task_module.AllenIntervalComposition(config=config)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append(f"Prompt: {prompt}")
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
