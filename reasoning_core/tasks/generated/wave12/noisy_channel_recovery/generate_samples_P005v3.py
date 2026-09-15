import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.noisy_channel_recovery.noisy_channel_recovery import (
    NoisyChannelRecovery,
)

random.seed(960070481)

OUT = Path(__file__).with_name("samples_P005v3.md")


def render(task, level):
    task.config.set_level(level)
    entry = task.generate_entry()
    prompt = task.render_prompt(entry.metadata)
    return prompt, entry.answer


def main():
    task = NoisyChannelRecovery()
    lines = []
    for level in [0, 2, 5]:
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            prompt, answer = render(task, level)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
