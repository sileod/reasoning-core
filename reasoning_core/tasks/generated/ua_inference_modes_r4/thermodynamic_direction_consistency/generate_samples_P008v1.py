import random
from pathlib import Path

import reasoning_core.tasks.generated.ua_inference_modes_r4.thermodynamic_direction_consistency.thermodynamic_direction_consistency as m

SEED = 682015719
random.seed(SEED)

OUT = Path(__file__).with_name("samples_P008v1.md")


def main():
    task = m.ThermodynamicDirectionConsistency()
    lines = ["# Samples for P008v1", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for k in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append(f"### Example {k}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(f"`{x.answer}`")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
