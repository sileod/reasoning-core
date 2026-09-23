import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_logic_r4.referential_action_cascade.referential_action_cascade import (
    Config,
    ReferentialActionCascade,
)


def main():
    random.seed(2072234021)
    task = ReferentialActionCascade()
    out = Path(__file__).with_name("samples_P005v2.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        cfg = Config()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(2):
            entry = task.generate_example()
            lines.append("Prompt:")
            lines.append(entry.metadata["_prompt"] if "_prompt" in entry.metadata else task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("Answer: " + entry.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
