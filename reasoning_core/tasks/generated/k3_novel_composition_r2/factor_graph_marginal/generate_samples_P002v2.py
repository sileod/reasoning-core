"""Seed 1336314872; regenerate with `python generate_samples_P002v2.py` from this directory."""
import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_novel_composition_r2.factor_graph_marginal.factor_graph_marginal import (
    FactorGraphMarginal,
)

SEED = 1336314872


def main():
    out = Path(__file__).with_name("samples_P002v2.md")
    task = FactorGraphMarginal()
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        for i in range(2):
            entry = task.generate_example()
            lines += [
                f"## Level {level}, Example {i + 1}",
                "",
                "### Prompt",
                "",
                "```text",
                task.render_prompt(entry.metadata),
                "```",
                "",
                "### Answer",
                "",
                "```text",
                entry.answer,
                "```",
                "",
            ]
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
