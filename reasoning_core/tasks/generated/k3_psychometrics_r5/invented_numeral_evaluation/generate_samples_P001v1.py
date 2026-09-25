import random
from pathlib import Path

random.seed(1662004003)

_ENTRY = "reasoning_core.tasks.generated.k3_psychometrics_r5.invented_numeral_evaluation.invented_numeral_evaluation"


def main():
    import importlib
    mod = importlib.import_module(_ENTRY)
    task = mod.InventedNumeralEvaluation()

    out_dir = Path(__file__).with_name("samples_P001v1.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")

    print("\n".join(lines))
    with open(out_dir, "w") as f:
        f.write("\n".join(lines))
    print(f"\nWrote {out_dir}")


if __name__ == "__main__":
    main()
