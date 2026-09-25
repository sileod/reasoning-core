import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_novel_composition_r4.stopped_sample_likelihood_ratio.stopped_sample_likelihood_ratio import (
    StoppedSampleConfig,
    StoppedSampleLikelihoodRatio,
)

SEED = 1336314872
OUT = Path(__file__).with_name("samples_P002v2.md")


def build():
    random.seed(SEED)
    task = StoppedSampleLikelihoodRatio()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        cfg = StoppedSampleConfig()
        cfg.set_level(level)
        task.config = cfg
        for i in range(2):
            entry = task.generate_entry()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f"## Example {i + 1}")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("Answer: " + entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    build()
