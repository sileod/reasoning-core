"""Generate samples_P006v1.md beside this module, byte-reproducible under seed."""

import random
from pathlib import Path

OUT = Path(__file__).with_name("samples_P006v1.md")

from reasoning_core.tasks.generated.k3_inference_modes_r4.truncated_series_operations.truncated_series_operations import (
    TruncatedSeriesOperations,
)

LEVELS = (0, 2, 5)
PER_LEVEL = 2


def render_one(task, level):
    task.config.set_level(level)
    x = task.generate_example()
    return task.render_prompt(x["metadata"]), x["answer"]


def main():
    random.seed(798610012)
    lines = []
    for level in LEVELS:
        lines.append(f"# Level {level}")
        task = TruncatedSeriesOperations()
        for _ in range(PER_LEVEL):
            prompt, answer = render_one(task, level)
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append(f"Answer: {answer}")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
