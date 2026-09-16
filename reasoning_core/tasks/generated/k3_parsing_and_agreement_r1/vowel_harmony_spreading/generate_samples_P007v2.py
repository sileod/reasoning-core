import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.vowel_harmony_spreading.vowel_harmony_spreading import (
    VowelHarmonySpreading,
)

SEED = 241712510
OUT = Path(__file__).with_name("samples_P007v2.md")


def main():
    random.seed(SEED)
    task = VowelHarmonySpreading()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for idx in range(2):
            e = task.generate_example()
            lines.append(f"**Example {idx + 1}**")
            lines.append("")
            lines.append("Prompt:")
            lines.append("```")
            lines.append(task.render_prompt(e.metadata))
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append(f"```\n{e.answer}\n```")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
