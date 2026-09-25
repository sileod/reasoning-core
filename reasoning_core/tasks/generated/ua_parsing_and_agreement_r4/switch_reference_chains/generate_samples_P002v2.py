import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_parsing_and_agreement_r4.switch_reference_chains.switch_reference_chains import (
    SwitchReferenceChains,
)


def main():
    random.seed(1336314872)
    task = SwitchReferenceChains()
    out = [f"# Samples for switch_reference_chains (P002v2)"]
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}")
        for _ in range(2):
            ex = task.generate_example()
            out.append("")
            out.append("Prompt:")
            out.append(ex.prompt)
            out.append("")
            out.append(f"Answer: {ex.answer}")
        out.append("")
    path = Path(__file__).with_name("samples_P002v2.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
