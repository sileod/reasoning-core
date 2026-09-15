import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.btree_promoted_key.btree_promoted_key import (
    BTreePromotedKey,
)

SEED = 1007633176


def main():
    random.seed(SEED)
    task = BTreePromotedKey()
    out = Path(__file__).with_name("samples_P006v2.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"Level {level}")
        lines.append("")
        for _ in range(2):
            task.config.set_level(level)
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
