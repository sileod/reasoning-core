import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from strip_fold_layer_order import StripFoldLayerOrder

random.seed(729651269)

task = StripFoldLayerOrder()
out_path = Path(__file__).with_name("samples_P005v1.md")

lines = []
lines.append("# Samples for P005v1: strip_fold_layer_order")
lines.append("")
lines.append("Assigned design choice: " + task.design_choice)
lines.append("")
lines.append("Each example shows the generated prompt verbatim and its gold answer.")
lines.append("")

for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    random.seed(729651269 + level)
    shown = 0
    while shown < 2:
        task.config.set_level(level)
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        lines.append(f"**Example {shown + 1}**")
        lines.append("")
        lines.append("Prompt:")
        lines.append("")
        for line in prompt.split("\n"):
            lines.append("    " + line)
        lines.append("")
        lines.append(f"Answer: {x.answer}")
        lines.append("")
        shown += 1

out_path.write_text("\n".join(lines))
print("wrote", out_path)
