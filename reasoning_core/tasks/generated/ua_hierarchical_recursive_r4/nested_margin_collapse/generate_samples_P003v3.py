import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_hierarchical_recursive_r4.nested_margin_collapse.nested_margin_collapse import (
    NestedMarginCollapse, NestedMarginCollapseConfig,
)


def main():
    random.seed(1259343118)
    t = NestedMarginCollapse()
    out = []
    for level in [0, 2, 5]:
        cfg = NestedMarginCollapseConfig()
        cfg.set_level(level)
        t.config = cfg
        out.append(f"## Level {level}")
        for _ in range(2):
            e = t.generate_entry()
            out.append("### Prompt")
            out.append(t.render_prompt(e.metadata))
            out.append("### Answer")
            out.append(e.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P003v3.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
