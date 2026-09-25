"""Generate samples_P004v1.md with two prompt/answer examples at levels 0, 2, 5.

Seed fixed so output is byte-reproducible.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_counterfactual_r4.qualitative_limit_path_dependence.qualitative_limit_path_dependence import (
    QualitativeLimitPathDependence,
)

random.seed(3536382515)


def main():
    task = QualitativeLimitPathDependence()
    out = Path(__file__).with_name("samples_P004v1.md")
    lines = []
    lines.append("# Samples for P004v1: qualitative_limit_path_dependence\n")
    lines.append(
        "Each entry shows the exact prompt the task emits and the gold answer underneath.\n"
    )
    for level in (0, 2, 5):
        lines.append(f"## Level {level}\n")
        task.config.set_level(level)
        for i in range(2):
            e = task.generate_example()
            lines.append(f"**Example {i+1}**\n")
            lines.append("Prompt:\n")
            lines.append("```\n" + e.metadata["prompt"] + "\n```\n")
            lines.append("Answer:\n")
            lines.append("```\n" + e.answer + "\n```\n")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
