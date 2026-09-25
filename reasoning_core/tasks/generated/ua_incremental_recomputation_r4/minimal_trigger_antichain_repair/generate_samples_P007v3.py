import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.minimal_trigger_antichain_repair.minimal_trigger_antichain_repair import (
    MinimalTriggerAntichainRepair,
)

random.seed(1034322864)

OUT = Path(__file__).with_name("samples_P007v3.md")
task = MinimalTriggerAntichainRepair()

sections = []
for level in (0, 2, 5):
    rows = []
    for _ in range(2):
        inst = MinimalTriggerAntichainRepair().config_cls()
        inst.set_level(level)
        t = MinimalTriggerAntichainRepair(config=inst)
        e = t.generate_entry()
        prompt = t.render_prompt(e.metadata)
        rows.append((prompt, e.answer))
    section = "\n\n".join(
        f"**Example {i + 1}**\n\nPrompt:\n```\n{p}\n```\n\nAnswer:\n```\n{a}\n```"
        for i, (p, a) in enumerate(rows)
    )
    sections.append(f"## Level {level}\n\n{section}")

md = "\n\n".join(sections) + "\n"
OUT.write_text(md)
print(f"wrote {OUT}")
