import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.probability_tree_marginal.probability_tree_marginal import (
    ProbabilityTreeMarginal,
)


def main():
    random.seed(3139243041)
    out = Path(__file__).with_name("samples_P010v1.md")
    task = ProbabilityTreeMarginal()
    lines = []
    lines.append("# ProbabilityTreeMarginal samples")
    lines.append("")
    for level in (0, 2, 5):
        lines.append("## Level %d" % level)
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append("Answer: %s" % ex.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
