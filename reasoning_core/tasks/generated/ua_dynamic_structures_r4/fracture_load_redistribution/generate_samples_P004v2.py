import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dynamic_structures_r4.fracture_load_redistribution.fracture_load_redistribution import (
    FractureLoadRedistribution,
)

SEED = 3577985643
OUT = Path(__file__).with_name("samples_P004v2.md")


def main():
    task = FractureLoadRedistribution()
    lines = []
    lines.append("# samples_P004v2")
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    random.seed(SEED)
    main()
