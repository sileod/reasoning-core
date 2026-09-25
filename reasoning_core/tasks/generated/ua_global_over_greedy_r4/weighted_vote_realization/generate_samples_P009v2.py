import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.weighted_vote_realization.weighted_vote_realization import (
    WeightedVoteRealization,
)

SEED = 2701974858
OUT = Path(__file__).with_name("samples_P009v2.md")


def main():
    random.seed(SEED)
    task = WeightedVoteRealization()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append("### Example")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
