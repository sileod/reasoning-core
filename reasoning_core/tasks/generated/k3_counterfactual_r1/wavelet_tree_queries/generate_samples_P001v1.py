"""Generate samples_P001v1.md for the wavelet_tree_queries trial."""

import random
from pathlib import Path

import reasoning_core.tasks.generated.k3_counterfactual_r1.wavelet_tree_queries.wavelet_tree_queries as wt

SEED = 1662004003
OUT = Path(__file__).with_name("samples_P001v1.md")


def main():
    random.seed(SEED)
    task = wt.WaveletTreeQueries()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        titles = {0: "l0a", 2: "l2a", 5: "l5a"}
        for idx in range(2):
            task.config.set_level(level)
            entry = task.generate_entry()
            lines.append(f"### Example {idx + 1}")
            lines.append("**Prompt:**")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
