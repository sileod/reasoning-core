import random
from pathlib import Path

random.seed(2701974858)

from reasoning_core.tasks.generated.k3_counterfactual_r1.consistent_hash_ring_churn.consistent_hash_ring_churn import (
    ConsistentHashRingChurn,
)


def main():
    task = ConsistentHashRingChurn()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append("## Level %d" % level)
        for i in range(2):
            entry = task.generate_example()
            out.append("### Example %d" % (i + 1))
            out.append("**Prompt:**")
            out.append("")
            out.append(task.render_prompt(entry.metadata))
            out.append("")
            out.append("**Answer:**")
            out.append("")
            out.append(entry.answer)
            out.append("")
    target = Path(__file__).with_name("samples_P009v2.md")
    target.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
