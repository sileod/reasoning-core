import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_counterfactual_r4.phylogenetic_network_reconciliation.phylogenetic_network_reconciliation import (
    phylo_network_reconciliation,
)

SEED = 368817805
OUT = Path(__file__).with_name("samples_P002v3.md")


def main():
    task = phylo_network_reconciliation()
    random.seed(SEED)
    lines = []
    lines.append("# phylogenetic_network_reconciliation samples")
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            entry = task.generate_example()
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
