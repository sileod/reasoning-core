import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.crdt_gossip_state_trace.crdt_gossip_state_trace import (
    CRDTGossipStateTrace,
)

SEED = 1475571465

random.seed(SEED)
task = CRDTGossipStateTrace()

out = Path(__file__).with_name('samples_P002v1.md')
blocks = []
for level in (0, 2, 5):
    task.config.set_level(level)
    blocks.append(f'## Level {level}')
    for i in range(2):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        blocks.append(f'### Example {i+1}')
        blocks.append(prompt)
        blocks.append(f'**Answer**: `{entry.answer}`')

out.write_text('\n\n'.join(blocks) + '\n')
