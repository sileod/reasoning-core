"""Generate seeded samples for P004v1: samples_P004v1.md."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.episodic_feature_binding_retrieval.episodic_feature_binding_retrieval import (
    EpisodicFeatureBindingRetrieval,
)


def main():
    random.seed(3536382515)
    task = EpisodicFeatureBindingRetrieval()
    out = ["# Samples for episodic_feature_binding_retrieval (P004v1)", ""]
    for level in (0, 2, 5):
        out.append("## Level %d" % level)
        out.append("")
        task.config.set_level(level)
        for _ in range(2):
            e = task.generate_example()
            out.append("### Example")
            out.append("")
            out.append(task.render_prompt(e.metadata))
            out.append("")
            out.append("Answer: %s" % e.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P004v1.md")
    path.write_text("\n".join(out), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
