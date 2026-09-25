import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r4.layered_interval_exposure.layered_interval_exposure import (
    LayeredIntervalExposure as Task,
)

SEED = 1475571465


def main():
    random.seed(SEED)
    out = Path(__file__).with_name("samples_P002v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        t = Task()
        for i in range(2):
            entry = t.generate_example(level=level)
            prompt = t.render_prompt(entry.metadata)
            lines.append(f"### Example {i+1}")
            lines.append("Prompt:")
            lines.append(prompt)
            lines.append("Answer:")
            lines.append(entry.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
