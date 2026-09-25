import random
from pathlib import Path

import reasoning_core.tasks.generated.ua_systematic_generalization_r4.branched_density_pushforward.branched_density_pushforward as mod

random.seed(682015719)

LEVELS = (0, 2, 5)
PER_LEVEL = 2

out = []
task = mod.BranchedDensityPushforward()
out.append("# samples_P008v1")
out.append("")
out.append(
    "Transport piecewise probability densities through noninjective maps by "
    "combining inverse-branch contributions and Jacobian factors; vary folds, "
    "flat regions, and composition, returning a density or atom mass."
)
out.append("")
out.append(f"(design_choice: {task.design_choice})")
out.append("")

for lev in LEVELS:
    out.append(f"## Level {lev}")
    out.append("")
    for _ in range(PER_LEVEL):
        entry = task.generate_example(level=lev)
        out.append("**Prompt:**")
        out.append("")
        out.append(entry.prompt)
        out.append("")
        out.append("**Answer:**")
        out.append("")
        out.append(entry.answer)
        out.append("")
        out.append("---")
        out.append("")

Path(__file__).with_name("samples_P008v1.md").write_text("\n".join(out))
print("wrote samples_P008v1.md")
