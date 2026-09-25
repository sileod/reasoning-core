import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_semantics_r4.lexical_event_coercion import (
    lexical_event_coercion as mod,
)

SEED = 1139467751

LEVELS = {0: 1, 2: 1, 5: 2}


def main():
    random.seed(SEED)
    out = []
    task = mod.LexicalEventCoercion()
    for level, depth in LEVELS.items():
        out.append(f"# Level {level}\n")
        task.config.depth = depth
        for i in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            out.append(f"## Example {i + 1}\n")
            out.append(prompt + "\n")
            out.append(f"**Answer:** {x.answer}\n")
        out.append("")
    Path(__file__).with_name("samples_P007v1.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
