import random
from pathlib import Path

random.seed(798610012)

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.wash_sale_basis_transport.wash_sale_basis_transport import (
    WashSaleBasisTransport,
)

task = WashSaleBasisTransport()

out = []
levels = [0, 2, 5]
for level in levels:
    task.config.set_level(level)
    out.append(f"# Level {level}\n")
    for _ in range(2):
        x = task.generate_example()
        out.append("Prompt:")
        out.append(task.render_prompt(x.metadata))
        out.append("")
        out.append(f"Answer: {x.answer}")
        out.append("")

path = Path(__file__).with_name("samples_P006v1.md")
path.write_text("\n".join(out))
print("wrote", path)
