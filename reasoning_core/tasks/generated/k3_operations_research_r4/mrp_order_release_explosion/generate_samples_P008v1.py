import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r4.mrp_order_release_explosion.mrp_order_release_explosion import (
    MrpOrderReleaseExplosion,
)


def main():
    random.seed(682015719)
    task = MrpOrderReleaseExplosion()
    sections = ["# P008v1 samples"]
    for level in (0, 2, 5):
        sections.append(f"## Level {level}")
        task.config.set_level(level)
        for number in (1, 2):
            entry = task.generate_entry()
            prompt = task.render_prompt(entry.metadata)
            sections.append(
                f"### Example {number}\n\n**Prompt:**\n```\n{prompt}\n```\n\n**Answer:**\n```\n{entry.answer}\n```")
    Path(__file__).with_name("samples_P008v1.md").write_text("\n\n".join(sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
