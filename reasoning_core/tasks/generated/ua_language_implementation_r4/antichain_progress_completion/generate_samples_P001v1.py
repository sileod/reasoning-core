import random
from pathlib import Path

random.seed(1662004003)

from reasoning_core.tasks.generated.ua_language_implementation_r4.antichain_progress_completion.antichain_progress_completion import (
    AntichainProgressCompletion,
)

OUT = Path(__file__).with_name("samples_P001v1.md")


def render_examples(levels):
    task = AntichainProgressCompletion()
    parts = []
    for level in levels:
        task.config.set_level(level)
        parts.append(f"### Level {level}")
        parts.append("")
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            parts.append("**Prompt**:")
            parts.append("")
            parts.append(prompt)
            parts.append("")
            parts.append("**Answer**: " + entry.answer)
            parts.append("")
    return "\n".join(parts)


def main():
    content = render_examples([0, 2, 5])
    OUT.write_text(content, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
