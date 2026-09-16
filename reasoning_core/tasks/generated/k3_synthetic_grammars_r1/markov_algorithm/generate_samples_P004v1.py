import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.markov_algorithm_execution.markov_algorithm import (
    MarkovAlgorithm,
)

SEED = 3536382515
LEVELS = (0, 2, 5)
PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = MarkovAlgorithm()
    out = Path(__file__).with_name("samples_P004v1.md")
    lines = ["# Markov Algorithm Execution - samples P004v1", ""]
    for level in LEVELS:
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(PER_LEVEL):
            entry = task.generate_example(level=level)
            lines.append(f"### Example {i + 1}")
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
