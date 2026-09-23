import random
from pathlib import Path

random.seed(1662004003)

from reasoning_core.tasks.generated.k3_state_tracking_r4.manacher_palindrome_radii.manacher_palindrome_radii import (
    ManacherPalindromeRadii,
)

OUT = Path(__file__).with_name("samples_P001v1.md")


def emit(task, level):
    task.config.set_level(level)
    e = task.generate_example()
    return task.render_prompt(e.metadata), e.answer.strip()


def main():
    random.seed(1662004003)
    task = ManacherPalindromeRadii()
    lines = ["# Samples for P001v1 (ManacherPalindromeRadii)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for idx in (1, 2):
            random.seed(1662004003 + level * 100 + idx)
            prompt, answer = emit(task, level)
            lines.append(f"### Example {idx}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append("```")
            lines.append(answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
