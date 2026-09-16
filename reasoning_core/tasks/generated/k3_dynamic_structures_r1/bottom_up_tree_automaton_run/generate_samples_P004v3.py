import random
from pathlib import Path

from reasoning_core.template import Task

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.bottom_up_tree_automaton_run.bottom_up_tree_automaton_run import (
    BottomUpTreeAutomatonRun,
)


def _render(task, metadata):
    return task.render_prompt(metadata)


def main():
    random.seed(1339177894)
    task = BottomUpTreeAutomatonRun()
    out = Path(__file__).with_name("samples_P004v3.md")
    parts = ["# samples_P004v3\n"]
    for level in (0, 2, 5):
        parts.append(f"\n## Level {level}\n")
        for i in range(2):
            ex = task.generate_example(level=level)
            parts.append(f"### Example {i + 1}\n")
            parts.append("Prompt:\n")
            parts.append("```\n" + _render(task, ex.metadata) + "\n```\n")
            parts.append("Answer:\n")
            parts.append("```\n" + ex.answer + "\n```\n")
    out.write_text("\n".join(parts))
    print(out)


if __name__ == "__main__":
    main()
