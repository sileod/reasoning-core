import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.canonical_huffman_code.canonical_huffman_code import (
    CanonicalHuffmanCode,
)

seed = 2881578109
random.seed(seed)

LEVELS = [0, 2, 5]
EXAMPLES_PER_LEVEL = 2


def main():
    out = Path(__file__).with_name("samples_P009v1.md")
    lines = ["# Samples for canonical_huffman_code (P009v1)", ""]
    for level in LEVELS:
        lines.append(f"## Level {level}")
        lines.append("")
        task = CanonicalHuffmanCode()
        task.config.set_level(level)
        for k in range(1, EXAMPLES_PER_LEVEL + 1):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f"### Example {k}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
