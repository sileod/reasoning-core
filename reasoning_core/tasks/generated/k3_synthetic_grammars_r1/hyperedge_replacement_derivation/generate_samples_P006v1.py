"""Write samples_P006v1.md with two complete prompt/answer examples at levels 0, 2, 5.

Seeded so the bytes are reproducible across processes.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.hyperedge_replacement_derivation.hyperedge_replacement_derivation import (
    HyperedgeReplacementDerivation,
)


def main():
    random.seed(798610012)
    task = HyperedgeReplacementDerivation()
    out = Path(__file__).with_name("samples_P006v1.md")
    lines = [
        "# Samples for hyperedge_replacement_derivation (P006v1)",
        "",
        "Each example states a hyperedge-replacement grammar (arity, productions), the",
        "start context edges and the addressed nonterminal edges; the answer is the",
        "sorted final edge list after replacing every nonterminal edge in address order.",
        "",
    ]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("## Level %d" % level)
        lines.append("")
        for i in range(2):
            entry = task.generate_example()
            lines.append("### Example %d" % (i + 1))
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(entry.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
