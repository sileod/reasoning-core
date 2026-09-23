import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_global_from_local_r4.ordered_rule_surface_derivation import (
    ordered_rule_surface_derivation as mod)

Task = mod.OrderedRuleSurfaceDerivation

random.seed(3867019559)
task = Task()

out = []
out.append("# samples_P009v1")
out.append("")
out.append("Task: ordered_rule_surface_derivation")
out.append("")
out.append("Ordered context-sensitive rewrite rules over invented segment inventories: "
           "derive a surface string from an underlying form, or decide whether swapping "
           "two rules' order (feeding/bleeding) changes the surface.")
out.append("")


def render(ex):
    return ex.prompt


for level in (0, 2, 5):
    out.append(f"## Level {level}")
    out.append("")
    generated = 0
    attempts = 0
    while generated < 2:
        attempts += 1
        ex = task.generate_example(level=level)
        out.append("### Example")
        out.append("")
        out.append("Prompt:")
        out.append("```")
        out.append(render(ex))
        out.append("```")
        out.append("")
        out.append("Answer:")
        out.append("```")
        out.append(ex.answer)
        out.append("```")
        out.append("")
        generated += 1

Path(__file__).with_name("samples_P009v1.md").write_text("\n".join(out))
print("\n".join(out))
