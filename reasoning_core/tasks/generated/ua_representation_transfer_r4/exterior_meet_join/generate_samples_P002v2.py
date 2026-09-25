import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_transfer_r4.exterior_meet_join.exterior_meet_join import (
    ExteriorMeetJoin,
)

random.seed(1336314872)

OUT = Path(__file__).with_name("samples_P002v2.md")

lines = []
lines.append("# Samples P002v2 - exterior_meet_join\n")


def emit(level):
    t = ExteriorMeetJoin()
    t.config.set_level(level)
    lines.append(f"## Level {level}\n")
    for _ in range(2):
        e = t.generate_example()
        lines.append("Prompt:")
        lines.append(t.render_prompt(e.metadata) + "\n")
        lines.append("Answer:")
        lines.append(e.answer + "\n")


for lv in (0, 2, 5):
    emit(lv)

OUT.write_text("\n".join(lines))
print("wrote", OUT)
