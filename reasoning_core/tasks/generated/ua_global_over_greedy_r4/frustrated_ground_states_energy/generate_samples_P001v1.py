import os
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.frustrated_interaction_ground_states.frustrated_interaction_ground_states import (
    FrustratedGroundStatesEnergy, FrustratedConfig,
)

random.seed(1662004003)


def main():
    task = FrustratedGroundStatesEnergy()
    out = []
    for level in (0, 2, 5):
        cfg = FrustratedConfig()
        cfg.set_level(level)
        task.config = cfg
        out.append("## Level {}".format(level))
        for i in range(2):
            ex = task.generate_example()
            out.append("### Example {}".format(i + 1))
            out.append("Prompt:")
            out.append(task.render_prompt(ex.metadata))
            out.append("Answer:")
            out.append(ex.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P001v1.md")
    path.write_text("\n".join(out) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
