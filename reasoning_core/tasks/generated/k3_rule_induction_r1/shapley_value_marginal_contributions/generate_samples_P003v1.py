import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_rule_induction_r1.shapley_value_marginal_contributions.shapley_value_marginal_contributions import (
    ShapleyValueMarginalContributions as T,
)


def main():
    random.seed(2267388306)
    out = Path(__file__).with_name("samples_P003v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task = T()
        task.config.set_level(level)
        for _ in range(2):
            entry = task.generate_example()
            lines.append("### Prompt")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("### Answer")
            lines.append(entry.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
