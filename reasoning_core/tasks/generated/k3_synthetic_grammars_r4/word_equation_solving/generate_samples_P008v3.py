import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_synthetic_grammars_r4.word_equation_solving.word_equation_solving import (
    WordEquationSolving,
)

SEED = 1618848011
LEVELS = (0, 2, 5)
EXAMPLES_PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = WordEquationSolving()
    lines = []
    for level in LEVELS:
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(EXAMPLES_PER_LEVEL):
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
    out = Path(__file__).with_name("samples_P008v3.md")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
