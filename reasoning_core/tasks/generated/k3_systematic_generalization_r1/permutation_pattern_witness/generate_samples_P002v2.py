import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.permutation_pattern_witness.permutation_pattern_witness import (
    PermutationPatternWitness,
)

SEED = 1336314872
OUT = Path(__file__).with_name("samples_P002v2.md")


def main():
    random.seed(SEED)
    task = PermutationPatternWitness()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}\n")
        for _ in range(2):
            e = task.generate_example()
            prompt = e.metadata.pop("_prompt", None) or task.render_prompt(e.metadata)
            answer = e.answer
            lines.append("### Example\n")
            lines.append("Prompt:\n")
            lines.append(prompt + "\n")
            lines.append("Answer:\n")
            lines.append(answer + "\n")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
