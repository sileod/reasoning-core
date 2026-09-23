"""Byte-reproducible sample generator for the P005v2 bandit simulation trial.

Seeds the module RNG once, then writes two verbatim prompt/answer examples at each
of levels 0, 2 and 5 into samples_P005v2.md next to this file.
"""

import random
from pathlib import Path

random.seed(2072234021)

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.fixed_rule_bandit_simulation.fixed_rule_bandit_simulation import (
    FixedRuleBanditSimulation,
)

LEVELS = (0, 2, 5)
PER_LEVEL = 2
out = Path(__file__).with_name("samples_P005v2.md")


def main():
    task = FixedRuleBanditSimulation()
    blocks = ["# P005v2 samples: fixed_rule_bandit_simulation", ""]
    for level in LEVELS:
        blocks.append(f"# Level {level}")
        blocks.append("")
        for _ in range(PER_LEVEL):
            ex = task.generate_example(level=level)
            blocks.append("Prompt:")
            blocks.append(ex.prompt)
            blocks.append("")
            blocks.append("Answer: " + ex.answer)
            blocks.append("")
    out.write_text("\n".join(blocks), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
