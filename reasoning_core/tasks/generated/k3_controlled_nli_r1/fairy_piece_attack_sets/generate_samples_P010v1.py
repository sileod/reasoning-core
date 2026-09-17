"""Generate samples_P010v1.md for fairy_piece_attack_sets (seed 2409743872)."""

from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r1.fairy_piece_attack_sets.fairy_piece_attack_sets import (
    FairyPieceAttackSets,
)


def main():
    import random

    random.seed(2409743872)
    out = []
    for level in (0, 2, 5):
        task = FairyPieceAttackSets()
        task.config.set_level(level)
        for i in range(2):
            x = task.generate_example()
            out.append(f"## Level {level} example {i + 1}\n")
            out.append("### Prompt\n")
            out.append(task.render_prompt(x.metadata))
            out.append("\n### Answer\n")
            out.append(x.answer)
            out.append("")
    text = "\n".join(out)
    path = Path(__file__).with_name("samples_P010v1.md")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
