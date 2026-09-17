import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_algorithms_and_data_structures_r1.temporal_connective_equivalence import (
    temporal_connective_equivalence as mod,
)


def main():
    random.seed(368817805)
    task = mod.TemporalConnectiveEquivalence()
    out = ["# Samples: temporal_connective_equivalence (P002v3)\n"]
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"\n## Level {level}\n")
        for i, label in enumerate(("yes", "no")):
            for _ in range(100):
                x = task.generate_example()
                if x.answer == label:
                    break
            else:
                raise RuntimeError("Could not sample both labels")
            out.append(f"\n### Example {i + 1}\n")
            out.append("Prompt:\n")
            out.append(task.render_prompt(x.metadata))
            out.append("\nAnswer:\n")
            out.append(x.answer)
    path = Path(__file__).with_name("samples_P002v3.md")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
