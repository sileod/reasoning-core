import random
from pathlib import Path

random.seed(1618848011)

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.constituency_dependency_conversion.constituency_dependency_conversion import (
    ConstituencyDependencyConversion,
)


def _make_task(level):
    t = ConstituencyDependencyConversion()
    t.config.set_level(level)
    return t


def main():
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        task = _make_task(level)
        for i in range(2):
            ex = task.generate_example()
            out.append(f"### Example {i + 1}")
            out.append("**Prompt:**")
            out.append("```")
            out.append(ex.prompt)
            out.append("```")
            out.append("**Answer:**")
            out.append("```")
            out.append(ex.answer)
            out.append("```")
            out.append("")
    path = Path(__file__).with_name("samples_P008v3.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
