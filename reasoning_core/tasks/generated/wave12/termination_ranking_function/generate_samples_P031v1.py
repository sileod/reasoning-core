import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.termination_ranking_function.termination_ranking_function import (
    TerminationRankingFunction,
)

random.seed(313472375)

OUT = Path(__file__).with_name("samples_P031v1.md")


def main():
    task = TerminationRankingFunction()
    lines = []
    lines.append("# Termination Ranking Function - samples P031v1")
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for k in range(2):
            ex = task.generate_entry()
            lines.append(f"### Example {k+1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
