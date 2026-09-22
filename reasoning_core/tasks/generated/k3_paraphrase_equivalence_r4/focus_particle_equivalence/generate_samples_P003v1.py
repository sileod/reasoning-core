import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r4.focus_particle_equivalence.focus_particle_equivalence import (
    FocusParticleEquivalence,
)

SEED = 2267388306
OUT = Path(__file__).with_name("samples_P003v1.md")

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(SEED)
    lines = ["# Samples for focus_particle_equivalence (P003v1)", ""]
    for level in sorted(LEVELS):
        t = FocusParticleEquivalence()
        t.config.set_level(level)
        lines.append("## Level %d" % level)
        lines.append("")
        for j in range(LEVELS[level]):
            e = t.generate_example()
            prompt = t.render_prompt(e.metadata)
            lines.append("#### Example %d" % (j + 1))
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            for pl in prompt.split("\n"):
                lines.append("    " + pl)
            lines.append("")
            lines.append("**Answer:** %s" % e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
