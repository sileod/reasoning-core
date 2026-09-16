import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.line_crossing_swap_schedule.line_crossing_swap_schedule import (
    LineCrossSwapSchedulev2,
)

random.seed(2072234021)


def main():
    task = LineCrossSwapSchedulev2()
    out = Path(__file__).with_name("samples_P005v2.md")
    blocks = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        blocks.append(f"## Level {level}\n")
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            blocks.append(prompt.strip())
            blocks.append("")
            blocks.append("Answer: " + entry.answer)
            blocks.append("")
    out.write_text("\n".join(blocks) + "\n")
    print(out)


if __name__ == "__main__":
    main()
