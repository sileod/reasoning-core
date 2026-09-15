import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_uncertainty_r1.network_reliability_factoring.network_reliability_factoring import (
    NetworkReliabilityFactoring,
)


def main():
    random.seed(729651269)
    out = Path(__file__).with_name("samples_P005v1.md")
    parts = []
    for level in (0, 2, 5):
        parts.append(f"## Level {level}")
        task = NetworkReliabilityFactoring()
        task.config.seed = 729651269
        task.config.set_level(level)
        for label in ("Example 1", "Example 2"):
            entry = task.generate_example()
            parts.append(f"### {label}")
            parts.append("Prompt:")
            parts.append(task.render_prompt(entry.metadata))
            parts.append("")
            parts.append("Answer:")
            parts.append(entry.answer)
            parts.append("")
    out.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()
