import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.coalitional_payoff_stability.coalitional_payoff_stability import CoalitionalPayoffStability


def main():
    random.seed(1475571465)
    task = CoalitionalPayoffStability()
    sections = ["# P002v1 samples"]
    for level in (0, 2, 5):
        sections.append(f"## Level {level}")
        task.config.set_level(level)
        for number in (1, 2):
            entry = task.generate_entry()
            prompt = task.render_prompt(entry.metadata)
            sections.append(
                f"### Example {number}\n\n**Prompt:**\n```\n{prompt}\n```\n\n"
                f"**Answer:**\n```\n{entry.answer}\n```"
            )
    Path(__file__).with_name("samples_P002v1.md").write_text(
        "\n\n".join(sections) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
