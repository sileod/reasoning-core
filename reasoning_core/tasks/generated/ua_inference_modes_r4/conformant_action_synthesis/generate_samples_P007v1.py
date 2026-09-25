import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.conformant_action_synthesis.conformant_action_synthesis import (
    ConformantActionSynthesis,
)

random.seed(1139467751)

TASK = ConformantActionSynthesis()


def main():
    out = []
    for level in (0, 2, 5):
        TASK.config.set_level(level)
        out.append(f"## Level {level}\n")
        for i in range(2):
            entry = TASK.generate_example()
            out.append(f"### Example {i + 1}\n")
            out.append("Prompt:\n")
            out.append(entry.prompt)
            out.append("\n")
            out.append(f"Answer: {entry.answer}\n")
            out.append("\n")
    path = Path(__file__).with_name("samples_P007v1.md")
    path.write_text("\n".join(out), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
