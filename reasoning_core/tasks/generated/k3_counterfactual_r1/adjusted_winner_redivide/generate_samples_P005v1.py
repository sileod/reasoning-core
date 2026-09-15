import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_counterfactual_r1.adjusted_winner_redivide.adjusted_winner_redivide import (
    AdjustedWinnerRedivide,
)


def _count_for(level):
    return 5 + level


def main():
    random.seed(729651269)
    out = []
    for level in (0, 2, 5):
        task = AdjustedWinnerRedivide()
        out.append(f"# Level {level}\n")
        for idx in range(2):
            ex = task.generate_example(level=level)
            out.append(f"### Example {idx + 1}\n")
            out.append(ex.prompt + "\n")
            out.append("Answer:\n")
            out.append(ex.answer + "\n")
    path = Path(__file__).with_name("samples_P005v1.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
