"""Generate samples_P005v1.md for the quantifier-dependency-strategy task."""

import random
from pathlib import Path

random.seed(729651269)

from quantifier_dependency_strategy import QuantifierDependencyStrategy

OUT = Path(__file__).with_name("samples_P005v1.md")


def family_exists_win_samples(family, count):
    t = QuantifierDependencyStrategy()
    for level in range(7):
        t.config.set_level(level)
        if t.config.family == family:
            found = []
            guard = 0
            while len(found) < count and guard < 2000:
                guard += 1
                entry = t.generate_example()
                found.append(entry)
            return found
    return []


def main():
    t = QuantifierDependencyStrategy()
    lines = []
    level_map = {0: "linear", 2: "branching", 5: "slashed"}
    for level, family in level_map.items():
        lines.append(f"# Level {level}\n")
        for _ in range(2):
            t.config.set_level(level)
            guard = 0
            while True:
                guard += 1
                entry = t.generate_example()
                if entry.metadata["family"] == family:
                    break
                if guard > 5000:
                    break
            prompt = t.render_prompt(entry.metadata)
            lines.append("### Example\n")
            lines.append(prompt.strip() + "\n")
            lines.append("\n**Answer:** " + entry.answer + "\n")
        lines.append("\n")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
