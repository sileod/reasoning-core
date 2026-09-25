import random
from pathlib import Path

import importlib

random.seed(525660630)

mod = importlib.import_module(
    "reasoning_core.tasks.generated.ua_global_over_greedy_r4."
    "representation_composition_multiplicity.representation_composition_multiplicity"
)

task = mod.RepCompositionMultiplicityV2()

out = []
for level, count in ((0, 2), (2, 2), (5, 2)):
    task.config.set_level(level)
    out.append(f"# Level {level}")
    for i in range(count):
        ex = task.generate_example()
        out.append("## Example " + str(i + 1))
        out.append("Prompt:")
        out.append(task.render_prompt(ex.metadata))
        out.append("Answer:")
        out.append(ex.answer)
        out.append("")

target = Path(__file__).with_name("samples_P011v2.md")
target.write_text("\n".join(out) + "\n")
print("wrote", target)
