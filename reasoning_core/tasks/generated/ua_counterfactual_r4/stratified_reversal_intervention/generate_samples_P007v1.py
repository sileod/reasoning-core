"""Generate samples_P007v1.md for the stratified reversal intervention task."""

import random
from pathlib import Path

random.seed(1139467751)

from reasoning_core.tasks.generated.ua_counterfactual_r4.stratified_reversal_intervention.stratified_reversal_intervention import (
    StratifiedReversalIntervention,
)


def main():
    task = StratifiedReversalIntervention()
    out = []
    out.append("# Samples P007v1 - stratified_reversal_intervention\n")
    for level in (0, 2, 5):
        out.append(f"## Level {level}\n")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            out.append(f"### Example {i + 1}\n")
            out.append("**Prompt:**\n")
            out.append(task.render_prompt(ex.metadata))
            out.append("\n")
            out.append("**Answer:**")
            out.append("")
            out.append(ex.answer)
            out.append("")
    md_path = Path(__file__).with_name("samples_P007v1.md")
    md_path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
