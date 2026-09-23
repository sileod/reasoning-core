import random
import random as rnd
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

random.seed(1662004003)
rnd.seed(1662004003)

from parallel_copy_sequentialization import ParallelCopySequentialization

OUT = Path(__file__).with_name("samples_P001v1.md")


def render_example(level):
    cfg = ParallelCopySequentialization.config_cls()
    cfg.set_level(level)
    task = ParallelCopySequentialization(config=cfg)
    entry = task.generate_example()
    prompt = task.render_prompt(entry.metadata)
    return prompt, entry.answer


def main():
    lines = []
    lines.append("# Parallel copy sequentialization samples\n")
    for level in (0, 2, 5):
        lines.append(f"## Level {level}\n")
        for i in range(2):
            prompt, answer = render_example(level)
            lines.append(f"### Example {i+1}\n")
            lines.append("**Prompt:**\n")
            lines.append("```\n" + prompt + "\n```\n")
            lines.append("**Answer:**\n")
            lines.append("```\n" + answer + "\n```\n")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
