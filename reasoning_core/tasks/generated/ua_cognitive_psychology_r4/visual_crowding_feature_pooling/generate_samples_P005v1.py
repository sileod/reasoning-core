import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.visual_crowding_feature_pooling.visual_crowding_feature_pooling import (
    VisualCrowdingFeaturePooling,
)

random.seed(729651269)

OUT = Path(__file__).with_name("samples_P005v1.md")

levels = {0: 2, 2: 2, 5: 2}
lines = []
for level, n in levels.items():
    lines.append("## Level {}\n".format(level))
    task = VisualCrowdingFeaturePooling()
    cfg = VisualCrowdingFeaturePooling.config_cls()
    cfg.apply_difficulty(level)
    task.config = cfg
    for _ in range(n):
        entry = task.generate_example()
        lines.append("Prompt:\n{}\n".format(task.render_prompt(entry.metadata)))
        lines.append("Answer:\n{}\n".format(entry.answer))

OUT.write_text("\n".join(lines))
print("wrote", OUT)
