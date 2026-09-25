import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r5.winding_region_repair.winding_region_repair import (
    WindingRegionRepair,
)

SEED = 798610012
OUT = Path(__file__).with_name("samples_P006v1.md")

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(SEED)
    task = WindingRegionRepair()
    lines = []
    lines.append("# Samples for P006v1: winding_region_repair")
    lines.append("")
    for level, count in LEVELS.items():
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for k in range(count):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append(f"### Example {k + 1}")
            lines.append("")
            lines.append("**Prompt**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
