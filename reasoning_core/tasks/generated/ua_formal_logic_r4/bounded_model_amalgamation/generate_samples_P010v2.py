import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r4.bounded_model_amalgamation.bounded_model_amalgamation import (
    BoundedModelAmalgamation,
)

random.seed(1211525277)
t = BoundedModelAmalgamation()

levels = [(0, 2), (2, 2), (5, 2)]
out = []
for lvl, cnt in levels:
    t.config.set_level(lvl)
    out.append(f"## Level {lvl}")
    for _ in range(cnt):
        e = t.generate_example()
        prompt = t.render_prompt(e.metadata)
        out.append(prompt)
        out.append(f"Answer: {e.answer}")
        out.append("")

path = Path(__file__).with_name("samples_P010v2.md")
path.write_text("\n".join(out) + "\n")
print(f"wrote {path}")
