import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_global_from_local_r4.threshold_cascade_fixpoint.threshold_cascade_fixpoint import (
    ThresholdCascadeFixpoint,
)

random.seed(3020341981)

OUT = Path(__file__).with_name("samples_P008v2.md")

task = ThresholdCascadeFixpoint()

with OUT.open("w") as f:
    for level in (0, 2, 5):
        task.config.set_level(level)
        f.write("## Level %d\n\n" % level)
        # gather two examples with varied modes
        shown = []
        attempts = 0
        need_modes = set()
        seen_modes = set()
        while len(shown) < 2 and attempts < 500:
            attempts += 1
            x = task.generate_example()
            mode = x.metadata['mode']
            if mode in seen_modes and len(seen_modes) < 2:
                continue
            seen_modes.add(mode)
            shown.append(x)
        for i, x in enumerate(shown):
            f.write("### Example %d\n\n" % (i + 1))
            f.write("**Prompt:**\n\n%s\n\n" % task.render_prompt(x.metadata))
            f.write("**Answer:**\n\n%s\n\n" % x.answer)
