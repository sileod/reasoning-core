import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.hereditary_base_rewrite.hereditary_base_rewrite import (
    HereditaryBaseRewrite,
)

random.seed(3867019559)


def main():
    task = HereditaryBaseRewrite()
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}\n")
        for idx in range(2):
            x = task.generate_example(level=level)
            out.append(f"### Example {idx + 1}\n")
            out.append(f"**Prompt:**\n\n```\n{x.prompt}\n```\n")
            out.append(f"**Answer:** `{x.answer}`\n")
        out.append("")
    text = "\n".join(out)
    dest = Path(__file__).with_name("samples_P009v1.md")
    dest.write_text(text)
    print(dest)


if __name__ == "__main__":
    main()
