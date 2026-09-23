import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_state_tracking_r4.dual_number_evaluation.dual_number_evaluation import (
    DualNumberEvaluation,
)


def main():
    random.seed(1339177894)
    out = Path(__file__).with_name("samples_P004v3.md")
    lines = []
    lines.append("# Dual number evaluation samples\n")
    for level in (0, 2, 5):
        t = DualNumberEvaluation()
        t.config.set_level(level)
        lines.append(f"## Level {level}\n")
        for _ in range(2):
            e = t.generate_example()
            prompt = t.render_prompt(e.metadata)
            lines.append("### Example\n")
            lines.append(prompt)
            lines.append("\n**Answer:**\n")
            lines.append(e.answer)
            lines.append("\n")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
