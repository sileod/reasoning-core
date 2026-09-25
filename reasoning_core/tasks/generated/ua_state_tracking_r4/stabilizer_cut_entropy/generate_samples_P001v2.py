import random
import sys
from pathlib import Path

from reasoning_core.tasks.generated.ua_state_tracking_r4.stabilizer_cut_entropy.stabilizer_cut_entropy import (
    StabilizerCutEntropy,
)

random.seed(2302342651)

LEVELS = [0, 2, 5]
PER_LEVEL = 2

lines = []
for level in LEVELS:
    t = StabilizerCutEntropy()
    t.config.set_level(level)
    for idx in range(PER_LEVEL):
        e = t.generate_example()
        prompt = t.render_prompt(e.metadata)
        lines.append(f'## Level {level}, example {idx+1}')
        lines.append('### Prompt')
        lines.append(prompt)
        lines.append('### Answer')
        lines.append(e.answer)
        lines.append('')

out = Path(__file__).with_name('samples_P001v2.md')
out.write_text('\n'.join(lines) + '\n')
print(f'wrote {out}')
