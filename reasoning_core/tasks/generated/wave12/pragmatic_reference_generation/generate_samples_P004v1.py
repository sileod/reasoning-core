import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.pragmatic_reference_generation.pragmatic_reference_generation import (
    PragmaticReferenceGeneration,
)

random.seed(1294949280)

OUT = Path(__file__).with_name("samples_P004v1.md")


def main():
    lines = []
    for level in (0, 2, 5):
        task = PragmaticReferenceGeneration()
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
