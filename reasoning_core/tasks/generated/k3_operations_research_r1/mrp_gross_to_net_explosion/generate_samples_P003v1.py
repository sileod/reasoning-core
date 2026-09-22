import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r1.mrp_gross_to_net_explosion.mrp_gross_to_net_explosion import MrpGrossToNetExplosion


def main():
    random.seed(2267388306)
    task = MrpGrossToNetExplosion()
    sections = ["# P003v1 samples"]
    for level in (0, 2, 5):
        sections.append(f"## Level {level}")
        task.config.set_level(level)
        for number in (1, 2):
            entry = task.generate_entry()
            prompt = task.render_prompt(entry.metadata)
            sections.append(f"### Example {number}\n\n**Prompt:**\n```\n{prompt}\n```\n\n**Answer:**\n```\n{entry.answer}\n```")
    Path(__file__).with_name("samples_P003v1.md").write_text("\n\n".join(sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
