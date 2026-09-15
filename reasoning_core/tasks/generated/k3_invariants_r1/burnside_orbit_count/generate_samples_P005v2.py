import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.burnside_orbit_count.burnside_orbit_count import (
    BurnsideOrbitCount,
    BurnsideOrbitCountConfig,
)

SEED = 2072234021
LEVELS = (0, 2, 5)
PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = BurnsideOrbitCount()
    out = []
    for level in LEVELS:
        cfg = BurnsideOrbitCountConfig()
        cfg.set_level(level)
        task.config = cfg
        out.append("## Level %d" % level)
        out.append("")
        for _ in range(PER_LEVEL):
            ex = task.generate_entry()
            prompt = task.render_prompt(ex.metadata)
            out.append("### Prompt")
            out.append("")
            out.append(prompt)
            out.append("")
            out.append("**Answer**: %s" % ex.answer)
            out.append("")
            assert task.score_answer(ex.answer, ex) == 1.0
    path = Path(__file__).with_name("samples_P005v2.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
