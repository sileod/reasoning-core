import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r4.nominal_equation_solving.nominal_equation_solving import (
    NominalEquationSolving,
)


def main():
    random.seed(1333628617)
    task = NominalEquationSolving()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for _ in range(6):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            out.append(prompt)
            out.append(f"Answer: {entry.answer}\n")
    out.append("")
    text = "\n".join(out)
    (Path(__file__).with_name("samples_P012v3.md")).write_text(text)


if __name__ == "__main__":
    main()
