import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_latent_representation_r4.mastermind_feedback_candidate_filtering import (
    mastermind_feedback_candidate_filtering as m,
)

SEED = 1662004003


def main():
    random.seed(SEED)
    task = m.MastermindFeedbackCandidateFiltering()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("## Level %d" % level)
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            lines.append("### Example %d (level %d)" % (i + 1, level))
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out = Path(__file__).with_name("samples_P001v1.md")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
