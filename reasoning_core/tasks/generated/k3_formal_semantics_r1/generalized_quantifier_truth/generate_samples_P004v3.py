import random
from pathlib import Path

random.seed(1339177894)

from generalized_quantifier_truth import GeneralizedQuantifierTruth

OUT = Path(__file__).with_name("samples_P004v3.md")


def main():
    lines = ["# Samples: generalized quantifier truth (P004v3)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task = GeneralizedQuantifierTruth()
        task.config.set_level(level)
        for i in range(2):
            entry = task.generate_entry()
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(OUT)


if __name__ == "__main__":
    main()
