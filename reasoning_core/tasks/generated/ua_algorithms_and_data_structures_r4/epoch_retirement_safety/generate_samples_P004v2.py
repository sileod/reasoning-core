import random
from pathlib import Path

random.seed(3577985643)

from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.epoch_retirement_safety.epoch_retirement_safety import (
    EpochRetirementSafety,
)

OUT = Path(__file__).with_name("samples_P004v2.md")


def render_examples(levels):
    task = EpochRetirementSafety()
    parts = []
    for level in levels:
        task.config.set_level(level)
        parts.append(f"### Level {level}")
        parts.append("")
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            parts.append("**Prompt**:")
            parts.append("")
            parts.append(prompt)
            parts.append("")
            parts.append("**Answer**: " + entry.answer)
            parts.append("")
    return "\n".join(parts)


def main():
    content = render_examples([0, 2, 5])
    OUT.write_text(content, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
