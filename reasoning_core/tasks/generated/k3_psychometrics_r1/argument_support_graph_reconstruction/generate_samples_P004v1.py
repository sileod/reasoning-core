import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_psychometrics_r1.argument_support_graph_reconstruction.argument_support_graph_reconstruction import ArgumentSupportGraphReconstruction


def main():
    random.seed(3536382515)
    out = Path(__file__).with_name("samples_P004v1.md")
    lines = ["# Samples: argument_support_graph_reconstruction (P004v1)", ""]
    for level in (0, 2, 5):
        cfg = ArgumentSupportGraphReconstruction.config_cls()
        cfg.set_level(level)
        task = ArgumentSupportGraphReconstruction(config=cfg)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            entry = task.generate_entry()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
