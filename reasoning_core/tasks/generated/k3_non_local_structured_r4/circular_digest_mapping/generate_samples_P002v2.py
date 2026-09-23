import random
from pathlib import Path

from circular_digest_mapping import CircularDigestMapping

random.seed(1336314872)

OUT = Path(__file__).with_name("samples_P002v2.md")


def main():
    lines = []
    lines.append("# samples_P002v2 - circular_digest_mapping")
    lines.append("")
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task = CircularDigestMapping()
        task.config.set_level(level)
        for i in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"```\n{x.answer}\n```")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
