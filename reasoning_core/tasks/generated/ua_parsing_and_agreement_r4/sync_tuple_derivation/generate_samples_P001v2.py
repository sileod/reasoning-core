import random
from pathlib import Path

random.seed(2302342651)

from reasoning_core.tasks.generated.ua_parsing_and_agreement_r4.synchronous_tuple_derivation.synchronous_tuple_derivation import (
    SyncTupleDerivationV2,
)

OUT = Path(__file__).with_name("samples_P001v2.md")


def main():
    task = SyncTupleDerivationV2()
    lines = ["# samples_P001v2: synchronous_tuple_derivation"]
    for level in (0, 2, 5):
        lines.append("")
        lines.append(f"## Level {level}")
        for _ in range(2):
            ex = task.generate_example(level=level)
            lines.append("")
            lines.append(f"**Prompt:**\n\n```\n{ex.prompt}\n```")
            lines.append("")
            lines.append(f"**Answer:** `{ex.answer}`")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
