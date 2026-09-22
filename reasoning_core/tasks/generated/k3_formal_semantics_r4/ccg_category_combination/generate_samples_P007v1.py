import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_semantics_r4.ccg_category_combination import (
    ccg_category_combination as mod,
)

SEED = 1139467751

LEVELS = {0: 2, 2: 4, 5: 7}


def main():
    random.seed(SEED)
    out = []
    task = mod.CcgCategoryCombination()
    for level, length in LEVELS.items():
        out.append(f"# Level {level}\n")
        task.config.seq_len = length
        for i in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            out.append(f"## Example {i + 1}\n")
            out.append(prompt + "\n")
            out.append(f"**Answer:** {x.answer}\n")
        out.append("")
    Path(__file__).with_name("samples_P007v1.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
