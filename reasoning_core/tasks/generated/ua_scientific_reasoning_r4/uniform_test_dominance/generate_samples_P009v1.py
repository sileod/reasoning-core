import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.uniform_test_dominance.uniform_test_dominance import (
    UniformTestDominance,
    UniformTestDominanceConfig,
)

SEED = 3867019559


def main():
    random.seed(SEED)
    task = UniformTestDominance()
    out = Path(__file__).with_name("samples_P009v1.md")
    lines = []
    lines.append("# Samples for uniform_test_dominance (P009v1)\n")
    for level in (0, 2, 5):
        cfg = UniformTestDominanceConfig()
        cfg.set_level(level)
        task.config = cfg
        lines.append(f"## Level {level}\n")
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append("**Prompt:**\n")
            lines.append("```")
            lines.append(prompt)
            lines.append("```\n")
            lines.append(f"**Answer:** {entry.answer}\n")
            lines.append("---\n")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
