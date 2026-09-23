import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_logic_r4.ehrenfeucht_fraisse_game \
    import ehrenfeucht_fraisse_game as m

random.seed(2701974858)

task = m.EhrenfeuchtFraisseV2()

out = ["# Ehrenfeucht-Fraisse game v2 - samples",
       "",
       "Assigned semantics: answer the winning player and, when Spoiler wins, the",
       "lexicographically smallest vertex pair (A-vertex, B-vertex) that guarantees",
       "Spoiler a win.",
       ""]

for level in (0, 2, 5):
    out.append(f"## Level {level}")
    out.append("")
    for i in range(2):
        ex = task.generate_example(level=level)
        out.append(f"### Example {i + 1}")
        out.append("")
        out.append("**Prompt:**")
        out.append("")
        out.append(ex.prompt)
        out.append("")
        out.append("**Answer:**")
        out.append("")
        out.append(ex.answer)
        out.append("")

out.append("")
Path(__file__).with_name("samples_P009v2.md").write_text("\n".join(out))
print("wrote samples_P009v2.md")
