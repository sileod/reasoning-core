import random
from pathlib import Path

from reasoning_core.template import Task

from pooled_test_status_decoding import PooledTestStatusDecode

SEED = 3536382515
OUT = Path(__file__).with_name("samples_P004v1.md")


def main():
    random.seed(SEED)
    task = PooledTestStatusDecode()
    lines = ["# Pooled test status decoding - samples",
             "",
             "Assignment: P004v1. Random seed 3536382515."]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("")
        lines.append(f"## Level {level}")
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append("")
            lines.append("**Prompt**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(entry.answer)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
