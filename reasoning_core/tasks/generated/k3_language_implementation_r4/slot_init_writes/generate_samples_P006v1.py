import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_language_implementation_r4.constructor_slot_initialization.constructor_slot_initialization import (
    SlotInitWrites,
)


def main():
    random.seed(798610012)
    out = Path(__file__).with_name("samples_P006v1.md")
    task = SlotInitWrites()
    blocks = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        blocks.append(f"## Level {level}\n")
        for idx in (1, 2):
            ex = task.generate_example()
            blocks.append(f"### Example {idx}\n")
            blocks.append("Prompt:\n")
            blocks.append("```\n" + ex.prompt + "\n```\n")
            blocks.append(f"**Answer:** {ex.answer}\n")
    out.write_text("\n".join(blocks))


if __name__ == "__main__":
    main()
