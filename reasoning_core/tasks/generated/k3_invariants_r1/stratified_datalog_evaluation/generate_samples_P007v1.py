import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.stratified_datalog_evaluation.stratified_datalog_evaluation import (
    StratifiedDatalogConfig,
    StratifiedDatalogEvaluation,
)

random.seed(1139467751)

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    out = Path(__file__).with_name("samples_P007v1.md")
    parts = ["# Samples for P007v1 (stratified_datalog_evaluation)", ""]
    for level, count in LEVELS.items():
        parts.append("## Level %d" % level)
        parts.append("")
        task = StratifiedDatalogEvaluation(
            StratifiedDatalogConfig(level=level, seed=random.randrange(2 ** 32))
        )
        for _ in range(count):
            e = task.generate_entry()
            parts.append("### Example")
            parts.append("")
            parts.append("**Prompt**")
            parts.append("")
            parts.append("```")
            parts.append(task.render_prompt(e.metadata))
            parts.append("```")
            parts.append("")
            parts.append("**Answer**")
            parts.append("")
            parts.append("```")
            parts.append(e.answer)
            parts.append("```")
            parts.append("")
    out.write_text("\n".join(parts))
    print("wrote", out)


if __name__ == "__main__":
    main()
