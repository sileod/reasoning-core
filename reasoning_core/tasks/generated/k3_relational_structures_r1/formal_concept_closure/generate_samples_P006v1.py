import random
from pathlib import Path

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from formal_concept_closure import (  # noqa: E402
    FormalConceptClosure,
    FormalConceptClosureConfig,
)

OUT = Path(__file__).with_name("samples_P006v1.md")


MODES = ["closure", "concepts", "implication"]


def collect(level, mode):
    t = FormalConceptClosure()
    cfg = FormalConceptClosureConfig()
    cfg.set_level(level)
    cfg.mode = mode
    cfg.apply_difficulty(level)
    t.config = cfg
    return t, t.generate_example()


def main():
    random.seed(798610012)
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        # show two distinct modes per level so all three modes appear across levels
        for i, mode in enumerate(MODES[level % 3:] + MODES[:level % 3][:1]):
            t, e = collect(level, mode)
            lines.append(f"### Example {i+1}")
            lines.append("**Prompt:**")
            lines.append(t.render_prompt(e.metadata).strip())
            lines.append("")
            lines.append("**Answer:**")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
