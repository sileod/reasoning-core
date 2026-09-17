import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.indexical_context_shifting.indexical_context_shifting import IndexicalContextShifting


def main():
    random.seed(729651269)
    task = IndexicalContextShifting()
    sections = ["# P005v1 samples"]
    for level in (0, 2, 5):
        task.config.set_level(level)
        sections.append(f"## Level {level}")
        for index in range(2):
            entry = task.generate_entry()
            prompt = task.render_prompt(entry.metadata)
            sections.append(f"### Example {index + 1}\n\n**Prompt:**\n```\n{prompt}\n```\n\n**Answer:**\n```\n{entry.answer}\n```")
    Path(__file__).with_name("samples_P005v1.md").write_text("\n\n".join(sections) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
