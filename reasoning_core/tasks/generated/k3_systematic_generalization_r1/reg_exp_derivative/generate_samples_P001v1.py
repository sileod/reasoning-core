import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.regular_expression_derivative.regular_expression_derivative import RegExpDerivative

SEED = 1662004003
LEVELS = (0, 2, 5)
PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = RegExpDerivative()
    out = []
    for level in LEVELS:
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for _ in range(PER_LEVEL):
            ex = task.generate_example()
            out.append("### Example\n")
            out.append("Prompt:\n")
            out.append("```\n")
            out.append(task.render_prompt(ex.metadata))
            out.append("```\n")
            out.append("Answer:\n")
            out.append("```\n" + str(ex.answer) + "\n```\n")
            out.append("\n")
    path = Path(__file__).with_name("samples_P001v1.md")
    path.write_text("\n".join(out), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
