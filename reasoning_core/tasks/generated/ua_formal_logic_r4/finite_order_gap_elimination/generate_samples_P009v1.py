import random
from pathlib import Path

from reasoning_core.template import Entry

from finite_order_gap_elimination import FiniteOrderGapElimination


def main():
    random.seed(3867019559)
    out = []
    levels = {0: 2, 2: 2, 5: 2}
    for level, count in levels.items():
        out.append(f"## Level {level}")
        out.append("")
        task = FiniteOrderGapElimination()
        task.config.set_level(level)
        for _ in range(count):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            out.append("**Prompt:**")
            out.append(prompt)
            out.append("")
            out.append("**Answer:**")
            out.append(ex.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P009v1.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
