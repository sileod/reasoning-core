import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_logic_r4.variance_override_validation.variance_override_validation import (
    VarianceOverrideValidation,
)


def main():
    random.seed(1139467751)
    task = VarianceOverrideValidation()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for example in _samples(task, 6):
            out.append(example)
    out.append("")
    text = "\n".join(out)
    (Path(__file__).with_name("samples_P007v1.md")).write_text(text)


def _samples(task, n):
    lines = []
    for _ in range(n):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        lines.append(prompt)
        lines.append(f"Answer: {entry.answer}\n")
    return lines


if __name__ == "__main__":
    main()
