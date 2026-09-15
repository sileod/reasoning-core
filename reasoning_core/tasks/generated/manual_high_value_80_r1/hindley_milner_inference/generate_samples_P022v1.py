import random
from pathlib import Path

from reasoning_core.template import Config

from reasoning_core.tasks.generated.manual_high_value_80_r1.hindley_milner_inference.hindley_milner_inference import (
    HindleyMilnerInference,
    HindleyMilnerConfig,
)


def main():
    random.seed(2451101752)
    task = HindleyMilnerInference()
    out = Path(__file__).with_name("samples_P022v1.md")
    lines = []
    cfg = HindleyMilnerConfig()
    for level in [0, 2, 5]:
        cfg.apply_difficulty(level)
        task.config = cfg
        lines.append("## Level %d\n" % level)
        for i in range(2):
            e = task.generate_entry()
            lines.append("Example %d\n" % (i + 1))
            lines.append("Prompt:\n\n%s\n\n" % task.render_prompt(e.metadata))
            lines.append("Answer:\n\n%s\n\n" % e.answer)
    out.write_text("\n".join(lines))
    print("wrote", out)


if __name__ == "__main__":
    main()
